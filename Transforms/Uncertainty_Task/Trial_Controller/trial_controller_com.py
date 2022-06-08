
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
BaseName = 'Trial Controller'   # The base name can have spaces.
NodeAttributeNames = ['Parameters', 'Trial Definition', 'Trial Result', 'Trial History']
NodeAttributeType = ['Static', 'Input', 'Output', 'Output']
ParameterNames = ['Visualisation', 'COM Port', 'Baud Rate', 'Reward Only After Lick', 'Start Delay', 'Odour Window',
                  'Pre Response Delay', 'Response Window', 'Reward Window', 'Inter Trial Range']
ParameterTypes = ['bool', 'str', 'int', 'bool', 'float', 'float', 'float', 'float', 'float', 'str']
ParametersDefaultValues = [False, 'COM4', 9600, False, 1.0, 1.0, 0.5, 1.0, 0.1, '1.0, 3.0']

WorkerDefaultExecutable = os.path.join(os.path.dirname(Exec), 'trial_controller_worker.py')
# </editor-fold>


# <editor-fold desc="The following code is called as its own process when the editor starts the graph.
#  You can refactor the name of the xxx_com variable but do not change anything else">
if __name__ == "__main__":
    transform_template_com = gu.start_the_transform_communications_process(NodeAttributeType, NodeAttributeNames)
    gu.register_exit_signals(transform_template_com.on_kill)
    transform_template_com.start_ioloop()

# </editor-fold>
