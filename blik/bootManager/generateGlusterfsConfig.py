#!/usr/bin/python
import sys

PORTAGE_PATH = '/usr/portage'
NODE_TYPE_PATH = '/opt/blik/images/%s'

def generateOneShare(share_name, share_path, backup_host):
    config = ''
    config += '# ------ %s share ------\n' % share_name
    config += 'volume %s-ds\n' % share_name
    config += '    type storage/posix\n'
    config += '    option directory %s\n' % share_path
    config += 'end-volume\n'
    config += '\n'

    config += 'volume %s-locks\n' % share_name
    config += '    type features/posix-locks\n'
    config += '    subvolumes %s-ds\n' % share_name
    config += 'end-volume\n'
    config += '\n'

    #backup volume
    config += 'volume %s-backup-ds\n' % share_name
    config += '    type protocol/client\n'
    config += '    option transport-type tcp/client\n'
    config += '    option remote-host %s\n' % backup_host
    config += '    ooption remote-subvolume %s-locks\n' % share_name
    config += '    option transport-timeout 5 # value in seconds\n'
    config += 'end-volume\n'
    config += '\n'

    #automatic file replication translator for dataspace
    config += 'volume %s-ds-afr\n' % share_name
    config += '    type cluster/afr\n'
    config += '    subvolumes %s-locks %s-backup-ds\n' % (share_name, share_name)
    config += 'end-volume\n'
    config += '\n'

    config += 'volume %s-client\n' % share_name
    config += '    type performance/io-threads\n'
    config += '    option thread-count 8\n'
    config += '    option cache-size 64MB\n'
    config += '    subvolumes %s-ds-afr\n' % share_name
    config += 'end-volume\n'
    config += '\n'

    return config

def generate(nodes_types, backup_host):
    config = ''
    config += '# GlusterFS config\n'

    config += generateOneShare('portage-tree', PORTAGE_PATH, backup_host)

    for node_type in nodes_types:
        config += generateOneShare('nt-%s'%node_type, NODE_TYPE_PATH % node_type, backup_host)

    subvolumes = 'portage-tree-client ' + ' '.join(['nt-%s'%n for n in nodes_types])

    config += 'volume server\n'
    config += '    type protocol/server\n'
    config += '    option transport-type tcp/server\n'
    config += '    subvolumes %s\n' % subvolumes
    config += '    option auth.addr.portage-tree-locks.allow 192.168.*.*,127.0.0.1\n'
    config += '    option auth.addr.portage-tree-client.allow 192.168.*.*,127.0.0.1\n'
    for node_type in nodes_types:
        config += '    option auth.addr.nt-%s-locks.allow 192.168.*.*,127.0.0.1\n' % node_type
        config += '    option auth.addr.nt-%s-client.allow 192.168.*.*,127.0.0.1\n' % node_type
    config += 'end-volume\n'
    config += '\n'

    return config


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'usage: generateGlusterfsConfig.py primary|backup <nodes_types> <output_file>'
        sys.exit(1)

    gen_type = sys.argv[1]
    nodes_types = sys.argv[2].split(',')
    output_file = sys.argv[3]

    if gen_type == 'primary':
        b_host = 'farnsworth-slave.blik.org'
    else:
        b_host = 'farnsworth-master.blik.org'

    config = generate(nodes_types, b_host)

    f = open(output_file, 'w')
    f.write(config)
    f.close()

    sys.exit(0)
