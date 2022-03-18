
# <editor-fold desc="The following 6 lines of code are required to allow Heron to be able to see the Operation without
# package installation. Do not change.">
import sys
from os import path
import cv2
import numpy as np

current_dir = path.dirname(path.abspath(__file__))
while path.split(current_dir)[-1] != r'Heron':
    current_dir = path.dirname(current_dir)
sys.path.insert(0, path.dirname(current_dir))
# </editor-fold>

# <editor-fold desc="Extra imports if required">
from Heron.communication.socket_for_serialization import Socket
from Heron import general_utils as gu, constants as ct
import copy
# </editor-fold>

# <editor-fold desc="Global variables if required. Global variables operate obviously within the scope of the process

vis: bool
block_length_ranges: list
lengths_block: list
reward_contingencies: list
current_block: list
correct_licks: list
# </editor-fold>


def initialise(worker_object):
    global vis
    global block_length_ranges
    global lengths_block
    global current_block
    global reward_contingencies
    global correct_licks

    try:
        parameters = worker_object.parameters
        vis = parameters[0]
        block_length_ranges_str = parameters[1]
        reward_contingencies_block1_str = parameters[2]
        reward_contingencies_block2_str = parameters[3]
    except:
        return False

    block_length_ranges = [int(i) for i in block_length_ranges_str.split(',')]
    create_new_block_sizes()
    current_block = [np.random.randint(0, 2) for i in np.arange(4)]
    reward_contingencies = [[float(i) for i in reward_contingencies_block1_str.split(',')],
                            [float(i) for i in reward_contingencies_block2_str.split(',')]]
    correct_licks = [0 for i in np.arange(4)]

    print(lengths_block, current_block, reward_contingencies)
    return True


def create_new_block_sizes(stim=None):
    global block_length_ranges
    global lengths_block

    if stim == None:
        lengths_block = [[np.random.randint(block_length_ranges[i], block_length_ranges[i + 1]) for i
                          in np.arange(0, 8, 2)] for i in np.arange(2)]
    else:
        s = int(stim)
        new_lengths = [np.random.randint(block_length_ranges[2 * s], block_length_ranges[2 * s + 1]) for i
                               in np.arange(2)]
        lengths_block[0][s] = new_lengths[0]
        lengths_block[1][s] = new_lengths[1]


def work_function(data, parameters):
    global vis
    global lengths_block
    global current_block
    global reward_contingencies
    global correct_licks

    vis = parameters[0]

    message = data[1:]  # data[0] is the topic
    message = Socket.reconstruct_array_from_bytes_message_cv2correction(message)

    # If the message comes from the Trial controller
    if len(message) == 2:
        # The Trial controller sends [previous_stim, correct_port_licks]
        previous_stim = message[0]
        correct_port_licks = message[1]

        # Add the number of correct licks to the current running sum
        correct_licks[previous_stim] = correct_licks[previous_stim] + correct_port_licks

        # If the number of correct licks reaches the block length of that stim then swap block
        # and zero the running sum of licks for that stim
        if correct_licks[previous_stim] == lengths_block[current_block[previous_stim]][previous_stim]:
            create_new_block_sizes(previous_stim)
            temp = copy.copy(current_block[previous_stim])
            current_block[previous_stim] = int(not current_block[previous_stim])
            correct_licks[previous_stim] = 0
            print('Changing block of stim {}, from block {} to block {}'.format(previous_stim,
                                                                                       temp,
                                                                                       current_block[previous_stim]))
            print('Current block lengths = {}'.format(lengths_block))

    current_stim = np.random.randint(0, 4)
    current_correct_reward_port_probability = reward_contingencies[current_block[current_stim]][current_stim]
    current_correct_reward_port = np.random.binomial(1, current_correct_reward_port_probability)

    result = [np.array([current_stim, current_correct_reward_port, current_block[current_stim]])]

    return result


# The on_end_of_life function must exist even if it is just a pass
def on_end_of_life():
    pass


if __name__ == "__main__":
    worker_object = gu.start_the_transform_worker_process(work_function=work_function,
                                                          end_of_life_function=on_end_of_life,
                                                          initialisation_function=initialise)
    worker_object.start_ioloop()
