# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL. and
# Cable Television Laboratories, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script is responsible for deploying Aricent_Iaas environments and
# Openstack Services
import logging

import os
import pkg_resources

__author__ = '_ARICENT'

logger = logging.getLogger('utils')


def add_ansible_hosts(config):
    """
     This will add the ansible hosts into the ansible hosts file placed at
     /etc/ansible/hosts
    """
    if config:
        logger.info(config)
        hosts = config
        host_str = ""
        host_file = open("/etc/ansible/hosts", "r+")
        file_content = ""
        for line in host_file:
            file_content = file_content + line
        for host in hosts:
            if host.get("ip")+" " in file_content:
                logger.info("")
            else:
                host_str = host.get("ip") + " ansible_ssh_user=" + host.get(
                    "username") + " ansible_ssh_pass=" + host.get(
                    "password") + "\n" + host_str
        logger.info(host_str)
        host_file.close()

        flag = False
        if host_str is not "":
            temp_file = open("/etc/ansible/hosts", "r+")
            for line in temp_file:
                if "[droplets]" in line:
                    flag = True
                    break
                else:
                    flag = False
            temp_file.close()
        host_file = open("/etc/ansible/hosts", "r+")
        file_content = ""
        for line in host_file:
            file_content = file_content + line

        if flag:
            host_file.write(host_str)
        elif host_str is not "":
            host_file.write("[droplets]" + "\n" + host_str)
        host_file.close()


def tenant_vlan(task):
    ret = None
    physical_network = task.get("physical_network")
    min_vlan_id = task.get("min_vlan_id")
    max_vlan_id = task.get("max_vlan_id")
    logger.info("physical network : "+physical_network)
    logger.info("min_vlan_id : "+str(min_vlan_id))
    logger.info("max_vlan_id : "+str(max_vlan_id))
    for host in task.get("HOSTS"):
        ip = host.get("ip")
        for interface in host.get("interfaces"):
            vlan_interface = interface.get("port_name")
            size = interface.get("size")
            if size is None:
                logger.error("Configure MTU size for Vlan")
                exit(1)
            else:
                vlan_pb_loc = pkg_resources.resource_filename(
                    'snaps_openstack.utilities.playbooks',
                    'vlan_playbook.yaml')

                ansible_command = "ansible-playbook " + vlan_pb_loc \
                                  + " --extra-vars=\'{\"vlan_interface\": \"" \
                                  + str(vlan_interface) + "\",\"target\": \"" \
                                  + ip + "\",\"min_vlan_id\": \"" + str(min_vlan_id) \
                                  + "\",\"max_vlan_id\": \"" + str(max_vlan_id) \
                                  + "\",\"physical_network\": \"" + str(physical_network) \
                                  + "\",\"size\": \"" + str(size) + "\"}\' "
                logger.info("launching ansible :" + ansible_command)
                os.system(ansible_command)

        restart_doc_pb_loc = pkg_resources.resource_filename(
            'snaps_openstack.utilities.playbooks', 'restartdoc.yaml')
        ansible_command_restart = "ansible-playbook " + restart_doc_pb_loc \
                                  + " --extra-vars=\'{\"target\": \"" + ip + "\"}\' "
        logger.info("launching ansible :" + ansible_command_restart)
        ret = os.system(ansible_command_restart)

    return ret


def tenant_vlan_clean(task):
    ret = None
    physical_network = task.get("physical_network")
    min_vlan_id = task.get("min_vlan_id")
    max_vlan_id = task.get("max_vlan_id")
    logger.info("physical network : "+physical_network)
    logger.info("min_vlan_id : "+str(min_vlan_id))
    logger.info("max_vlan_id : "+str(max_vlan_id))
    for host in task.get("HOSTS"):
        ip = host.get("ip")
        for interface in host.get("interfaces"):
            vlan_interface = interface.get("port_name")
            size = interface.get("size")
            if size is None:
                logger.error("Configure MTU size for Vlan")
                exit(1)
            else:
                vlan_pb_loc = pkg_resources.resource_filename(
                    'snaps_openstack.utilities.playbooks',
                    'vlan_cleanup_playbook.yaml')

                ansible_command = "ansible-playbook " + vlan_pb_loc \
                                  + " --extra-vars=\'{\"vlan_interface\": \"" \
                                  + str(vlan_interface) + "\",\"target\": \"" \
                                  + ip + "\",\"min_vlan_id\": \"" + str(min_vlan_id) \
                                  + "\",\"max_vlan_id\": \"" + str(max_vlan_id) \
                                  + "\",\"physical_network\": \"" + str(physical_network) \
                                  + "\",\"size\": \"" + str(size) + "\"}\' "
                logger.info("launching ansible :" + ansible_command)
                os.system(ansible_command)

        restart_doc_pb_loc = pkg_resources.resource_filename(
            'snaps_openstack.utilities.playbooks', 'restartdoc.yaml')
        ansible_command_restart = "ansible-playbook " + restart_doc_pb_loc \
                                  + " --extra-vars=\'{\"target\": \"" + ip + "\"}\' "
        logger.info("launching ansible :" + ansible_command_restart)
        ret = os.system(ansible_command_restart)

    return ret


def mtu(task):
    ret = None

    for host in task.get("HOSTS"):
        ip = host.get("ip")
        for interface in host.get("interfaces"):
            size = interface.get("size")
            port = interface.get("port_name")
            mtu_pb_loc = pkg_resources.resource_filename(
                'snaps_openstack.utilities.playbooks',
                'physical_mtu.yaml')

            ansible_command = "ansible-playbook " + mtu_pb_loc + " -i \"" \
                              + ip + ",\"  --extra-vars=\'{\"size\": \"" \
                              + size + "\",\"interface\": \"" + port + "\"}\'"
        logger.info(ansible_command)
        ret = os.system(ansible_command)

    return ret
