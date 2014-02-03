#
# blik.nodesManager.plugins contain operations plugins packages
#
# Every plugin pakage in __init__.py package should contain OPERATIONS_PLUGINS variable
# OPERATIONS_PLUGINS format:  {'<operation_name>' : (PluginClass1, ...), ...}
#
# Every plugin class should be inherited from OperationPlugin class (defined in blik.nodesManager.operationsPluginManager)
#
# Note: don't forget import OperationPlugin class as following:
#       from blik.nodesManager.operationsPlugin import OperationPlugin
#
# Note: don't forget import plugin class before use it in OPERATIONS_PLUGINS structure 
#

from base_operations import *

OPERATIONS_PLUGINS = {
                        'SYNC':     (SynchronizeOperation,),
                        'REBOOT':   (RebootOperation,)
                     }
