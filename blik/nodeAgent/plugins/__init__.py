#
#Update OPERATIONS_PLUGINS for usage custom plugins
#
#OPERATIONS_PLUGINS format:  {'<operation_name>' : PluginClass1, ...}
#
#Note: don't forget import plugin class before use it in OPERATIONS_PLUGINS structure 
#

from blik.nodeAgent.plugins.base_operations import *

OPERATIONS_PLUGINS = {
        'SYNC': SynchronizeOperation,
        'REBOOT': RebootOperation,
        'GET_NODE_INFO': GetNodeInfoOperation,
        'MOD_HOSTNAME': ChangeHosnameOperation
        }
