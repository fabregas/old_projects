#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodeAgent.agentPlugin
@author Konstantin Andrusenko
@date August 12, 2011

This module contains the implementation of PluginManager class.
"""

from blik.utils.friBase import FriCaller
from blik.utils.logger import logger

FARNSWORTH_HOSTNAME='farnsworth_master' #hostname of management node
NODES_MANAGER_PORT=1989

WAIT_TIMEOUT = 10 #wait for connect to management node (in seconds)

class NodeAgentPlugin:
    def __init__(self, session_id, node):
        '''
        DON'T REIMPLEMENT THIS CONSTRUCTOR
        '''
        self.__session_id = session_id
        self.__node = node

    def updateOperationProgress(self, progress_percent, ret_message='', ret_code=0, ret_params={}):
        '''
        Updating operation progress. Send progress information to management node by FRI protocol
                                    DON'T REIMPLEMENT THIS METHOD

        @progress_percent (integer) - operation progress in percents (100 = finished operation)
        @ret_code (integer) - indicate state of operation processing
                                (if 0 then already ok, else operation is failed)
        @ret_message (string) - description of operation progress
        @ret_params (dict {param_name: param_value}) - return parameters
        '''
        fri_caller = FriCaller()

        packet = {  'id': self.__session_id,
                    'node': self.__node,
                    'progress': progress_percent,
                    'ret_code': ret_code,
                    'ret_message': ret_message,
                    'ret_parameters': ret_params}

        code, message = fri_caller.call(FARNSWORTH_HOSTNAME, packet, NODES_MANAGER_PORT, timeout=WAIT_TIMEOUT)

        if code:
            logger.error('%s.updateOperationProgress failed with code=%s and message=%s'%
                            (self.__class__.__name__, code, message))



    def process(self, parameters):
        '''
        Process operation on node side. Should be reimplemented in child class for implement
        custom operation logic
        You should use updateOperationProgress method for update operation progress

        @parameters (dict {param_name: param_value}) - input operation parameters values
        '''
        pass

