#!/usr/bin/python
import sys
import re
import uuid
import os

CLUSTER_DIR = '~/virtual-clusters'

def generate_cluster(cluster_name, machines_count, memory, iface):
    uuid_prefix =  str(uuid.uuid1())[:-2]
    cluster_spec_dir = os.path.join(CLUSTER_DIR, cluster_name)
    commands = ['mkdir -p %s'%cluster_spec_dir]
    del_commands = []
    start_commands = []
    stop_commands = []

    for num in range(machines_count):
        hostname = '%s%02i'%(cluster_name, num)
        commands.append('VBoxManage createvm --name %s --register --basefolder %s --uuid %s%02i'%(hostname, cluster_spec_dir, uuid_prefix, num))
        commands.append('VBoxManage modifyvm %s%02i --memory %s --pae on --boot1 net --nic1 bridged --cableconnected1 on --bridgeadapter1 %s --audio none'%(cluster_name, num,memory, iface))
        start_commands.append('VBoxManage startvm %s --type headless'%hostname)
        stop_commands.append('VBoxManage controlvm %s poweroff'%hostname)
        del_commands.append('VBoxManage unregistervm %s%02i'%(uuid_prefix, num))

    del_commands.append('rm -rf %s'%cluster_spec_dir)
    return commands, del_commands, start_commands, stop_commands

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stdout.write('usage: %s generate <cluster_name> [<nodes count>] [<memory>] [<iface>]\n'%sys.argv[0])
        sys.exit(1)

    command = sys.argv[1]
    cluster_name = sys.argv[2]
    if not re.match('^[\w-]+$', cluster_name):
        sys.stderr.write('Cluster name has invalid format. Supported characters: [a-zA-Z0-9_-]\n')
        sys.exit(1)

    if command == 'generate':
        machines_count = 1
        memory = 128
        iface = 'eth0'

        if len(sys.argv) > 3:
            machines_count = int(sys.argv[3])
        if len(sys.argv) > 4:
            memory = int(sys.argv[4])
        if len(sys.argv) > 5:
            iface = sys.argv[5]

        commands, del_commands, start_commands, stop_commands = generate_cluster(cluster_name, machines_count, memory, iface)

        f = open('%s_register.sh'%cluster_name, 'w')
        for command in commands:
            f.write('%s\n'%command)
        f.close()

        f = open('%s_remove.sh'%cluster_name, 'w')
        for command in del_commands:
            f.write('%s\n'%command)
        f.close()

        f = open('%s_start.sh'%cluster_name, 'w')
        for command in start_commands:
            f.write('%s\n'%command)
        f.close()

        f = open('%s_stop.sh'%cluster_name, 'w')
        for command in stop_commands:
            f.write('%s\n'%command)
        f.close()

        print('Scripts for cluster management saved to current directory into %s_*.sh files.'%cluster_name)
    else:
        sys.stderr.write('Command "%s" is not supported\n'%command)
        sys.exit(1)

