
# <editor-fold desc="The following 9 lines of code are required to allow Heron to be able to see the Operation without
# package installation. Do not change.">
import os
import sys
from os import path

current_dir = path.dirname(path.abspath(__file__))
while path.split(current_dir)[-1] != r'Heron':
    current_dir = path.dirname(current_dir)
sys.path.insert(0, path.dirname(current_dir))

from Heron import general_utils as gu
Exec = os.path.abspath(__file__)
# </editor-fold>

# <editor-fold desc="The following code is called from the GUI process as part of the generation of the node.
# It is meant to create node specific elements (not part of a generic node).
# This is where a new node's individual elements should be defined">
"""
Properties of the generated Node
"""
BaseName = 'Trials Generator'  # The base name can have spaces.
NodeAttributeNames = ['Parameters', 'Start / Previous Trial Result', 'Trial Definition']
NodeAttributeType = ['Static', 'Input', 'Output']
ParameterNames = ['Visualisation',
                  'Blocks Length Range\n(S1Min, S1Max, S2Min, S2Max, S3Min, S3Max, S4Min, S4Max)',
                  'Reward Contingencies Block 1\n(Stim 1, Stim 2, Stim 3, Stim 4)',
                  'Reward Contingencies Block 2\n(Stim 1, Stim 2, Stim 3, Stim 4)']
ParameterTypes = ['bool', 'str', 'str', 'str']
ParametersDefaultValues = [False, '1,3, 2,4, 3,5, 4,6', '0.75, 0, 0.75, 0.25', '0.25, 1, 0.75, 0.25']

WorkerDefaultExecutable = os.path.join(os.path.dirname(Exec), 'trial_generator_worker.py')
# </editor-fold>


# <editor-fold desc="The following code is called as its own process when the editor starts the graph.
#  You can refactor the name of the xxx_com variable but do not change anything else">
if __name__ == "__main__":
    trial_generator_com = gu.start_the_transform_communications_process(NodeAttributeType, NodeAttributeNames)
    gu.register_exit_signals(trial_generator_com.on_kill)
    trial_generator_com.start_ioloop()

# </editor-fold>
