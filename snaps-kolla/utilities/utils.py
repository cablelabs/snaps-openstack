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

# This script is responsible for deploying Aricent_Iaas environments and Openstack Services
import argparse
import logging
import os
import re
import sys
from optparse import OptionParser
sys.path.append("../common/utils" )
import file_utils
import yaml
import fileinput



__author__ = '_ARICENT'

logger = logging.getLogger('launch_provisioning')

ARG_NOT_SET = "argument not set"

def __addansiblehosts(config):
   """
    This will add the ansible hosts into the ansible hosts file placed at /etc/ansible/hosts
   """
   if config:
      logger.info(config)
      hosts=config
      host_str=""
      host_file=open("/etc/ansible/hosts","r+")
      file_content=""
      for line in host_file:
        file_content=file_content+line
      for host in hosts:
        if host.get("ip") in file_content:
          logger.info("")
        else:
          host_str=host.get("ip")+" ansible_ssh_user="+host.get("username")+" ansible_ssh_pass="+host.get("password")+"\n"+host_str
      logger.info(host_str)
      host_file.close()

      flag=False
      if host_str is not "":
        textToSearch = "[droplets]"
        tempFile=open("/etc/ansible/hosts","r+")
        for line in tempFile:
          if "[droplets]" in line :
            flag=True
            break
          else:
            flag= False
        tempFile.close()
      host_file=open("/etc/ansible/hosts","r+")
      file_content=""
      for line in host_file:
          file_content=file_content+line


      if flag:
         host_file.write(host_str)
      elif host_str is not "":
         host_file.write("[droplets]"+"\n"+host_str)
      host_file.close()


def __tenant_vlan(task):
    for host in task.get("HOSTS"):
        ip=host.get("ip")
        for interface in host.get("interfaces"):
            vlan_interface=interface.get("port_name")
            vlan_id=str(interface.get("vlan_id"))
            ansible_command="ansible-playbook playbooks/vlan_playbook.yaml  --extra-vars=\'{\"vlan_interface\": \""+str(vlan_interface)+"\",\"target\": \""+ip+"\",\"vlan_id\": \""+str(vlan_id)+"\"}\' "
            logger.info("launching ansible :"+ ansible_command)
            ret=os.system(ansible_command)
        ansible_command_restart="ansible-playbook playbooks/restartdoc.yaml  --extra-vars=\'{\"target\": \""+ip+"\"}\' "
        logger.info("launching ansible :"+ ansible_command_restart)
        ret=os.system(ansible_command_restart)

    return ret
def __mtu(task):
   ret= False
   for host in task.get("HOSTS"):
     ip=host.get("ip")
     for interface in host.get("interfaces"):
       size=interface.get("size")
       port=interface.get("port_name")
       ansible_command="ansible-playbook playbooks/physical_mtu.yaml -i \""+ip+",\"  --extra-vars=\'{\"size\": \""+size+"\",\"interface\": \""+port+"\"}\'"
       logger.info(ansible_command)
       ret=os.system(ansible_command)
   return ret

def main(arguments):
    """
     This will launch the provisioning of Bare metat & IaaS.
     There is pxe based configuration defined to provision the bare metal.
     For IaaS provisioning different deployment models are supported.
     Relevant conf files related to PXE based Hw provisioning & Openstack based IaaS must be present in ./conf folder.
     :param command_line options: This expects command line options to be entered by user for relavant operations.
     :return: To the OS
    """

    log_level = logging.INFO
    if arguments.log_level != 'INFO':
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    logger.info('Launching Utils Operation ........')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    export_path=dir_path+"/"
    os.environ['CWD_IAAS']=export_path
    print "===========================Current Exported Relevant Path=================================="
    logger.info(export_path)

    config = file_utils.read_yaml(arguments.config)
    logger.info('Read configuration file - ' + arguments.config)
    try:
          if args.tenant_vlan is not ARG_NOT_SET:
             for task in config.get("TASKS"):
                if task.get("name")=="TenantVLAN":
                  logger.info("Performing Task "+task.get('name')+" with arguments")
                  logger.info( "--tenant_vlan")
                  __addansiblehosts(task.get("HOSTS"))
                  ret=__tenant_vlan(task)
                  ret=0
                  if  ret==0:
            	     logger.info('Completed opeartion successfully')
                  else:
              	     logger.info('Error while performing operation')
          if args.mtu is not ARG_NOT_SET:
             for task in config.get("TASKS"):
                if task.get("name")=="mtu":
                  logger.info("Performing Task "+task.get('name')+" with arguments")
                  logger.info( "--mtu")
                  __addansiblehosts(task.get("HOSTS"))
                  ret=__mtu(task)
                  ret=0
                  if  ret==0:
                     logger.info('Completed opeartion successfully')
                  else:
                     logger.info('Error while performing operation')

    except Exception as e:
           logger.error('Unexpected error deploying environment. Rolling back due to - ' + e.message)
           raise e


if __name__ == '__main__':


#    if os.environ.get('CWD_IAAS') is None:
#         path=os.getcwd()

#         print'ENVIRONMENT VARIABLE "CWD_IAAS" IS NOT EXPORTED OR USER IS NOT ROOT USER : USE COMMAND: su root; export CWD_IAAS="'+path+ "\""
#         exit(1)

    # To ensure any files referenced via a relative path will begin from the diectory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='config', required=True,
                        help='The configuration file in YAML format - REQUIRED', metavar="FILE")
    parser.add_argument('-l', '--log-level', dest='log_level', default='INFO', help='Logging Level (INFO|DEBUG)')
    parser.add_argument('-tvlan', '--tenant_vlan', dest='tenant_vlan', nargs='?', default=ARG_NOT_SET,
                        help='When used, deployment and provisioning of openstack will be started')
    parser.add_argument('-mtu', '--mtu', dest='mtu', nargs='?', default=ARG_NOT_SET,
                        help='When used, sets the mtu size on nic')
    args = parser.parse_args()

    if  args.tenant_vlan is ARG_NOT_SET and\
        args.config is ARG_NOT_SET:
        logger.info('Must enter -tvlan  for configuring vlan based tenant networks')
        exit(1)
#    if args.presingleNIC is not ARG_NOT_SET and args.postsingleNIC is not ARG_NOT_SET and args.tenant_vlan is not ARG_NOT_SET:
#        print 'Cannot enter multiple options -prenic/--pre_single_NIC or -prenic/--post_single_NIC or -tvlan/--tenant_vlan'
#        exit(1)

    main(args)
