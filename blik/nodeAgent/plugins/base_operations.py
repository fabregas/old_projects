
from blik.nodeAgent.agentPlugin import NodeAgentPlugin
from blik.utils.exec_command import run_command
import os
import time

CONFIG_FILE = '/home/node_agent/.node_config'

class SynchronizeOperation(NodeAgentPlugin):
    def process(self, parameters):
        try:
            f = open(CONFIG_FILE, 'w')

            for key,value in parameters.items():
                f.write('%s = %s\n'%(key,value))

            f.close()

            self.updateOperationProgress(100, ret_message='Node parameters is synchronized')
        except Exception, err:
            self.updateOperationProgress(70, ret_message='Synchronization config failed: %s'%err, ret_code=1)


class RebootOperation(NodeAgentPlugin):
    def process(self, parameters):
        try:
            code, cout, cerr = run_command(['reboot'])

            if code:
                raise Exception('Reboot operation failed: %s'%cerr)

            self.updateOperationProgress(100, ret_message='Node is rebooting now...')
        except Exception, err:
            self.updateOperationProgress(50, ret_message='Error occured: %s'%err, ret_code=1)


class GetNodeInfoOperation(NodeAgentPlugin):
    def __get_meminfo_map(self, lines):
        ret_map = {}
        for line in lines:
            key, value = line.split(':')

            ret_map[key.strip()] = value.split()[0] # this may be defect if value is not kB

        return ret_map


    def process(self, parameters):
        try:
            ret_params = {}

            #get load avarage (5, 10 and 15 minutes)
            lavg = open('/proc/loadavg').read()
            lavgs = lavg.split()

            ret_params['loadavg_5'] = lavgs[0]
            ret_params['loadavg_10'] = lavgs[1]
            ret_params['loadavg_15'] = lavgs[2]

            #get memory info
            meminfo_lines = open('/proc/meminfo').readlines()
            meminfo = self.__get_meminfo_map(meminfo_lines)

            ret_params['mem_total'] = meminfo['MemTotal']
            ret_params['mem_free'] = meminfo['MemFree']
            ret_params['buffers'] = meminfo['Buffers']
            ret_params['cached'] = meminfo['Cached']
            ret_params['swap_cached'] = meminfo['SwapCached']
            ret_params['swap_total'] = meminfo['SwapTotal']
            ret_params['swap_free'] = meminfo['SwapFree']

            #get uptime
            uptime = open('/proc/uptime').read()
            uptime = uptime.split()[0]
            ret_params['uptime'] = uptime

            self.updateOperationProgress(100, ret_message='Node information is collected', ret_params=ret_params)
        except Exception, err:
            self.updateOperationProgress(70, ret_message='Getting node info failed: %s'%err, ret_code=1)


