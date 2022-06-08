
# <editor-fold desc="The following 6 lines of code are required to allow Heron to be able to see the Operation without
# package installation. Do not change.">
import sys
import time
from os import path
import cv2
import numpy as np

current_dir = path.dirname(path.abspath(__file__))
while path.split(current_dir)[-1] != r'Heron':
    current_dir = path.dirname(current_dir)
sys.path.insert(0, path.dirname(current_dir))
# </editor-fold>

# <editor-fold desc="Extra imports if required">
import serial
import datetime
from Heron.communication.socket_for_serialization import Socket
from Heron import general_utils as gu, constants as ct
# </editor-fold>

# <editor-fold desc="Global variables if required. Global variables operate obviously within the scope of the process
# that is running when this script is called so they pose no existential threats and are very useful in keeping state
# over different calls of the work function (see below).">
vis: bool
com_port: str
baud_rate: int
respond_after_lick: bool
start_delay:float
odour_window:float
pre_response_delay:float
response_window: float
reward_window: float
inter_trial_window: float
arduino_serial: serial.Serial
trial_number: int

#stim_on_commands = [i.encode('utf-8') for i in ['q', 'e', 't', 'u']]
stim_on_commands = [i.encode('utf-8') for i in ['q']]
#stim_off_commands = [i.encode('utf-8') for i in ['w', 'r', 'y', 'i']]
stim_off_commands = [i.encode('utf-8') for i in ['w']]
reward_on_commands = [i.encode('utf-8') for i in ['a', 'd']]
reward_off_commands = [i.encode('utf-8') for i in ['s', 'f']]
# </editor-fold>


def initialise(worker_object):
    global vis
    global com_port
    global baud_rate
    global respond_after_lick
    global start_delay
    global odour_window
    global pre_response_delay
    global response_window
    global reward_window
    global inter_trial_window
    global arduino_serial
    global trial_number

    # put the initialisation of the Node's parameter's in a try loop to take care of the time it takes for the GUI to
    # update the TransformWorker object.
    try:
        parameters = worker_object.parameters
        vis = parameters[0]
        com_port = parameters[1]
        baud_rate = parameters[2]
        respond_after_lick = parameters[3]
        start_delay = parameters[4]
        odour_window = parameters[5]
        pre_response_delay = parameters[6]
        response_window = parameters[7]
        reward_window = parameters[8]
        inter_trial_window = [float(i) for i in parameters[9].split(',')]
    except:
        return False

    try:
        arduino_serial = serial.Serial(port=com_port, baudrate=baud_rate, timeout=response_window/10)
    except:
        print('Cannot connect to arduino port {}'.format(com_port))
        return False

    trial_number = 0

    return True


def get_lick_from_arduino():
    global arduino_serial

    arduino_response = arduino_serial.read()
    arduino_serial.reset_input_buffer()
    arduino_serial.reset_output_buffer()
    lick = int(arduino_response.decode('utf-8'))

    return lick


def read_arduino(reward_port):
    time_start = time.perf_counter()
    time_current = time.perf_counter()

    correct_port_lick = 0

    start_response_time = now()

    if vis:
        print('Reading Arduino to check for licks')
    arduino_serial.timeout = response_window
    while (time_current - time_start) < response_window:
        try:
            bytes_in_buffer = arduino_serial.in_waiting
            if bytes_in_buffer > 0:
                lick = get_lick_from_arduino()
                if vis:
                    print('Lick = {}'.format(lick))
                if lick == reward_port:
                    correct_port_lick = 1
            else:
                pass
        except:
            pass

        time_current = time.perf_counter()
        gu.accurate_delay(100)

    return correct_port_lick, start_response_time


def reward(correct_port_lick, reward_port):
    if vis:
        print('Has correct Port been Licked: {}'.format(correct_port_lick == True))

    start_reward_time = now()
    if vis:
        print(' ==== Arduino Reward On {}'.format(reward_on_commands[reward_port]))
    arduino_serial.write(reward_on_commands[reward_port])

    end_reward_time = now()
    if vis:
        print(' ==== Arduino Reward Off {}'.format(reward_on_commands[reward_port]))
    arduino_serial.write(reward_off_commands[reward_port])

    return start_reward_time, end_reward_time


def now():
    return str(datetime.datetime.now())


def work_function(data, parameters):
    global vis
    global respond_after_lick
    global start_delay
    global odour_window
    global pre_response_delay
    global response_window
    global reward_window
    global inter_trial_window
    global trial_number

    trial_number += 1

    try:
        vis = parameters[0]
    except:
        pass

    # Get message in from previous Node
    message = data[1:]  # data[0] is the topic
    message = Socket.reconstruct_array_from_bytes_message_cv2correction(message)

    stim = message[0]
    reward_port = message[1]
    block_of_stim = message[2]

    if vis:
        print('============= Starting Trial {} ============'.format(trial_number))
        print('Current Stim = {}, current correct reward port = {}'.format(stim, reward_port))

    start_trial_time = now()

    if vis:
        print(' ooo Waiting Start Delay {}'.format(start_delay))
    gu.accurate_delay(start_delay * 1000)

    open_stim_time = now()

    if vis:
        print(' ==== Arduino Open Stim {}'.format(stim))
    arduino_serial.write(stim_on_commands[stim])

    if vis:
        print('ooo Starting Odour Delay {}'.format(odour_window))
    gu.accurate_delay(odour_window * 1000)

    close_stim_time = now()
    if vis:
        print(' === Arduino Close Stim {}'.format(stim))
    arduino_serial.write(stim_off_commands[stim])

    if vis:
        print('ooo Starting Pre-Response Delay {}'.format(pre_response_delay))
    gu.accurate_delay(pre_response_delay * 1000)

    correct_port_lick, start_response_time = read_arduino(reward_port)

    if respond_after_lick and correct_port_lick:
        start_reward_time, end_reward_time = reward(correct_port_lick, reward_port)
    elif respond_after_lick and not correct_port_lick:
        if vis:
            print(" ooo Correct port hasn't been licked = No reward")
        start_reward_time = datetime.datetime.now()
        end_reward_time = start_reward_time
    elif not respond_after_lick:
        start_reward_time, end_reward_time= reward(correct_port_lick, reward_port)

    if vis:
        print('ooo Starting Response Delay {}'.format(reward_window))
    gu.accurate_delay(reward_window * 1000)

    iti = np.random.uniform(inter_trial_window[0], inter_trial_window[1])

    if vis:
        print('ooo Starting ITI Delay {}'.format(iti))

    gu.accurate_delay(iti * 1000)

    end_iti_time = now()

    result = [np.array([stim, correct_port_lick]),
              np.array([start_trial_time, open_stim_time, close_stim_time, start_response_time,
                        start_reward_time, end_reward_time, end_iti_time,
                        str(stim), str(reward_port), str(block_of_stim), str(correct_port_lick)])]

    if vis:
        print(' ooo Stim and Correct Port Lick = {}'.format(result[0]))
        print('============== Ended Trial {} ================'.format(trial_number))
        print('----------------------------------------------')

    return result


# The on_end_of_life function must exist even if it is just a pass
def on_end_of_life():
    pass


if __name__ == "__main__":
    worker_object = gu.start_the_transform_worker_process(work_function=work_function,
                                                          end_of_life_function=on_end_of_life,
                                                          initialisation_function=initialise)
    worker_object.start_ioloop()
