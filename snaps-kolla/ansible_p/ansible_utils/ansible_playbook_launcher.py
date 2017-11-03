# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL. and Cable Television Laboratories, Inc.
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

#This script is responsible for calling all the playbooks responsible for deploying openstack services

import logging

from collections import namedtuple

import os
#import paramiko
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
import ansible.constants
#from ansible.executor.playbook_executor import PlaybookExecutor
#from ansible.parsing.dataloader import DataLoader
#from ansible.vars import VariableManager
#from ansible.inventory import Inventory
#import ansible.constants

__author__ = '_ARICENT'

logger = logging.getLogger('ansible_playbook_operations')
def __deploy_ansible_playbook_prepare(playbook_path,user,password,PROXY_PATH,dpdk):
    """
    This method calls the preparation playbook for devstack which is responsible for all the installation and creation of Stack user
    :param playbook_path: path to the devstak_preparation playbook
    :param user: username or the hostname of the current node
    : param password: password assosiated to the current host
    : return :t/f: true if successful
    """
    if not playbook_path:
      return False

    if not user:
      return False

    if not password:
      return False
    logger.info("Applying Ansible Playbooks")
    cwd = os.getcwd()
    rel_dir = os.path.dirname(playbook_path)
 #  os.chdir(rel_dir)
    os.system('pwd')
    os.system('/usr/bin/ansible-playbook '+ playbook_path+ ' --inventory=ansible_p/commission/openstack/playbooks/deploy_mode/devstack/temp.ini --extra-vars=\'{\"PROXY_PATH\": \"'+PROXY_PATH+'\",\"dpdk\": \"'+dpdk+'\"}\'')
    os.chdir(cwd)
    return True

def __deploy_ansible_playbooksi_os(ip, playbook_path, local_conf_path ,user,password, host_name,iface,PROXY_PATH,isolcpu,reserved_host_memory_mb,dpdk) :

    """
    Applies ansible playbooks to the listed hosts with provided IPs
    :param ansible_configs: a list of Ansible host configurations
    :param playbook_path: the path of the playbook  file
    :return: t/f - true if successful
    """

    logger.info("Applying Ansible Playbooks")
#    cwd = os.getcwd()
#    rel_dir = os.path.dirname(playbook_path)
#   os.chdir(rel_dir)
    command = '/usr/bin/ansible-playbook '+ playbook_path +' --inventory=ansible_p/commission/openstack/playbooks/deploy_mode/devstack/temp.ini --extra-vars=\'{\"local_conf_path\": \"'+local_conf_path+'\",\"target\": \"'+ip+'\",\"host_name\": \"'+host_name+'\",\"if_name\": \"'+iface+'\",\"pin_set\": \"'+isolcpu+'\",\"dpdk\": \"'+dpdk+'\",\"reserved_host_memory_mb\": \"'+reserved_host_memory_mb+'\",\"PROXY_PATH\": \"'+PROXY_PATH+'\"}\''
    logger.info(command)
 #  os.chdir(cwd)
    os.system(command)
    return True

def __deploy_ansible_playbook_cleanup(ip, playbook_path,user,password,PROXY_PATH):

    """
    Applies ansible playbooks to the listed hosts with provided IPs
    :param ansible_configs: a list of Ansible host configurations
    :param playbook_path: the path of the playbook  file
    :return: t/f - true if successful
    """

    command = '/usr/bin/ansible-playbook '+ playbook_path +' --inventory=ansible_p/commission/openstack/playbooks/deploy_mode/devstack/temp.ini --extra-vars=\'{\"target\": \"'+ip+'\",\"PROXY_PATH\": \"'+PROXY_PATH+'\"}\''
    logger.debug(command)
    os.system(command)
    return True

def __launch_ansible_playbook(list_ip, playbook, extra_variable=None, proxy_setting=None):
    """
    Applies an Ansible playbook
    :param playbook: the playboo to be applied
    """
    if not os.path.isfile(playbook):
        raise Exception('Requested playbook is not found - ' + playbook)

    if not playbook:
         logger.warn('Unable to find playbook - ' + playbook)

    #ansible.constants.HOST_KEY_CHECKING = False

    variable_manager = VariableManager()
    #variable_manager.extra_vars =  None
    #if extra_variable is not None


    if extra_variable is not None:
     variable_manager.extra_vars = extra_variable
     logger.info(extra_variable)
    else:
     logger.info('NO EXTRA VARS')
    loader = DataLoader()
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=list_ip)
    variable_manager.set_inventory(inventory)
    ssh_extra_args = None
    if proxy_setting and proxy_setting.ssh_proxy_cmd:
        ssh_extra_args = '-o ProxyCommand=\'' + proxy_setting.ssh_proxy_cmd + '\''

    options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path',
                                     'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                     'become', 'become_method', 'become_user', 'verbosity', 'check', 'sftp_extra_args', 'scp_extra_args'])

    ansible_opts = options(listtags=None, listtasks=None, listhosts=None, syntax=False, connection='ssh',
                           module_path=None, forks=100, remote_user=None, private_key_file=None,
                           ssh_common_args=None, ssh_extra_args=None, become=True, become_method='sudo',
                           become_user=None, verbosity=11111, check=False,sftp_extra_args=None, scp_extra_args=None)

    logger.debug('Setting up Ansible Playbook Executor for playbook - ' + playbook)
    executor = PlaybookExecutor(
        playbooks=[playbook],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=ansible_opts,
        passwords=None)

    logger.debug('Executing Ansible Playbook - ' + playbook)
    ret= executor.run()
    return ret
