
import threading
import time
import socket
import struct
import fcntl
import crypt
import string
import os
from random import choice
from blik.utils import friBase
from blik.utils.logger import logger
from blik.utils.exec_command import run_command

MANAGEMENT_SERVER = 'farnsworth.blik.org'
LISTENER_PORT = 1986

SLEEP_SENDER_TIME = 5
SALT = 'fabregas_salt'

class BootEventSenderThread(threading.Thread):
    def _remount_devfs(self):
        #FIXME: I dont know why /dev mouned AFTER /dev/pts and /dev/shm, but its fact :(
        os.system('umount /dev/pts')
        os.system('umount /dev/shm')
        os.system('mount -av')

    def _set_new_hostname(self, uuid):
        hostname = 'NODE-%s' % uuid.split('-')[-1]

        run_command(['hostname',hostname])

        ret,out,err = run_command(['dhcpcd','eth0'])
        if ret:
            raise Exception('dhcpcd eth0 error: %s'%err)

        return hostname

    def _get_interface_info(self):
        ifname = 'eth0'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        mac = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

        ip_address = socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,  # SIOCGIFADDR
                        struct.pack('256s', ifname[:15]))[20:24])

        return mac, ip_address

    def _get_uuid(self):
        ret,out,err = run_command(['dmidecode', '-s', 'system-uuid'])
        if ret:
            raise Exception('dmidecode error: %s'%err)

        return out.strip()

    def _create_user(self):
        user = 'node_agent'
        password = ''.join([choice(string.letters + string.digits) for i in range(20)])
        run_command(['useradd', '-m', 'node_agent'])
        enc_passwd = crypt.crypt(password, SALT)
        ret, out, err = run_command(['usermod', '-p', enc_passwd, 'node_agent'])

        if ret:
            raise Exception('usermod error: %s'%err)

        return user, password

    def _get_hardware_info(self):
        ret,out,err = run_command(['uname', '-p'])
        if ret:
            raise Exception('uname error: %s'%err)

        processor = out.strip()

        all_memory = open('/proc/meminfo').readlines()[0]
        all_memory = all_memory.split(':')[1]
        all_memory, mesure = all_memory.strip().split(' ')
        all_memory = int(all_memory)
        if mesure.lower() == 'kb':
            all_memory /= 1024
        elif mesure.lower() == 'gb':
            all_memory *= 1024

        return  processor, all_memory

    def stop(self):
        self.stoped = True

    def run(self):
        try:
            self.stoped = False

            uuid = self._get_uuid()
            hostname = self._set_new_hostname(uuid)
            mac_address, ip_address = self._get_interface_info()
            login, password = self._create_user()
            processor, memory = self._get_hardware_info()

            caller = friBase.FriCaller()
            packet = {  'uuid': uuid,
                        'hostname': hostname,
                        'ip_address': ip_address,
                        'mac_address': mac_address,
                        'login': login,
                        'password': password,
                        'processor': processor,
                        'memory': memory }

            logger.info('BOOT EVENT: %s'%packet)

            while not self.stoped:
                code,msg = caller.call(MANAGEMENT_SERVER, packet, LISTENER_PORT)

                if code != 0:
                    logger.error('Boot event send error: %s'%msg)
                else:
                    break

                time.sleep(SLEEP_SENDER_TIME)

            return code
        except Exception, err:
            logger.error("Boot event sender error: %s"%err)
