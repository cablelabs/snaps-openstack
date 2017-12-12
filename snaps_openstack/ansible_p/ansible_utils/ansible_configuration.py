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

#This script is responsible for preparing all the files and variables neede for devstack deployment and calling the user defined  methods for the devstack  deployment
import re
import yaml
import shutil
import ansible_playbook_launcher
import os
import logging
import sys
#Change the system path to import consts file
from snaps_openstack.common.consts import consts

DEFAULT_REPLACE_EXTENSIONS = None

logger = logging.getLogger('deploy_ansible_configuration')

def file_replace(fname, pat, s_after):
    """
    This method is responsible for replacing the version in devstack_preparation.yaml
    :param fname
    :param pat
    :param s_after

    """
    # first, see if the pattern is even in the file.
    logger.debug("Replacing version in devstack_preparation.yaml")
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def provision_preparation(list_ip, proxy_dict, git_branch, user_dict, deployment_type,dpdk):
 """
 This method is responsible for writing the hosts info in ansible hosts file proxy inf in ansible proxy file
 set the git branch version in devstack_preparation_file
 : param list_ip : list of all th ip
 : param proxy_dict: proxy data in the dictionary format
 : param git_branch : git branch version for the openstack
 : user_dict : user credential in dictionary format
 : return ret :
 """

 ## code which adds ip to the /etc/anisble/hosts file
 ret=False
 group_found=False
 deployment_type = deployment_type.lower()


 if proxy_dict:
   logger.debug("Adding proxies")
   proxy_file_in = open(consts.PROXY_DATA_FILE,"r+")
   proxy_file_in.seek(0)
   proxy_file_in.truncate()
   proxy_file_out = open(consts.PROXY_DATA_FILE,"w")
   proxy_file_out.write("---")
   proxy_file_out.write("\n")
   for key,value in proxy_dict.iteritems():
              logger.debug("Proxies added in file:"+key+":"+value)
              proxy_file_out.write(key+": "+str(value)+"\n")
   proxy_file_out.close()
   proxy_file_in.close()
 if not user_dict:
    return ret





def clean_up_kolla(list_ip,git_branch,docker_registry,docker_port,service_list, operation, second_storage):
 """
 This method is responsible for the cleanup of openstack services
 :param list_ip: all the ip of nodes in list format
 :param cred_dict: user credentials in dictionary format
 : return ret :
 """
 playbook_path_cleanup_hosts=consts.KOLLA_CLEANUP_HOSTS
 playbook_path_remove_registry=consts.KOLLA_REMOVE_REGISTRY
 playbook_path_remove_storage=consts.KOLLA_REMOVE_STORAGE
 playbook_path_remove_images=consts.KOLLA_REMOVE_IMAGES
 PROXY_DATA_FILE=consts.PROXY_DATA_FILE
 VARIABLE_FILE=consts.VARIABLE_FILE
 BASE_FILE_PATH=consts.KOLLA_SOURCE_PATH
 if list_ip:
  ret=ansible_playbook_launcher.__launch_ansible_playbook(list_ip,playbook_path_cleanup_hosts,{'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE, 'GIT_BRANCH':git_branch})
  if(ret!=0):
    logger.info('FAILED IN CLEANUP')
    exit(1)
  if('cinder' in service_list):
   ret_storage=ansible_playbook_launcher.__launch_ansible_playbook(list_ip,playbook_path_remove_storage,{'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE, 'BASE_FILE_PATH':BASE_FILE_PATH, 'SECOND_STORAGE': second_storage})
   if(ret_storage!=0):
    logger.info('FAILED')
    exit(1)
   if( operation is "cleanregistry") :
     ret1=ansible_playbook_launcher.__launch_ansible_playbook(list_ip,playbook_path_remove_registry,{'target': docker_registry,'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE})
     if(ret1!=0):
        logger.info('Regsitery cleanup problems might be there')
     ret_image=ansible_playbook_launcher.__launch_ansible_playbook(list_ip,playbook_path_remove_images,{'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE})
     if(ret_image!=0):
        logger.info('Image cleanup problems might be there')


def launch_provisioning_kolla(iplist,git_branch,cred_dict,host_name_map,host_node_type_map,docker_registry,docker_port,kolla_base,kolla_install,ext_sub,ext_gw,ip_pool_start,ip_pool_end,second_storage, operation, hostCpuMap, reserve_memory,base_size,count,default,vxlan):
 ret = False
 playbook_path_sethosts=consts.KOLLA_SET_HOSTS
 playbook_path_sethostname=consts.KOLLA_SET_HOSTSNAME
 playbook_path_launch_single_node=consts.SINGLE_NODE_KOLLA_YAML
 playbook_path_launch_compute=consts.MULTI_NODE_KOLLA_COMPUTE_YAML
 playbook_path_launch_controller=consts.MULTI_NODE_KOLLA_CONTROLLER_YAML
 playbook_path_launch_iso_nw=consts.MULTI_NODE_KOLLA_ISO_NWK_YAML
 playbook_path_launch_storage=consts.KOLLA_SET_STORAGE
 playbook_path_set_registry=consts.KOLLA_SET_REGISTRY
 playbook_path_set_kolla=consts.KOLLA_SET_KOLLA
 playbook_path_copy_key=consts.KOLLA_COPY_KEY
 playbook_path_push_key=consts.KOLLA_PUSH_KEY
 playbook_path_ceph_setup=consts.KOLLA_CEPH_SETUP
 playbook_path_launch_compute_pike=consts.MULTI_NODE_KOLLA_COMPUTE_YAML_PIKE
 playbook_path_launch_controller_pike=consts.MULTI_NODE_KOLLA_CONTROLLER_YAML_PIKE
 playbook_path_launch_single_node_pike=consts.SINGLE_NODE_KOLLA_YAML_PIKE
 playbook_path_launch_set_pin=consts.KOLLA_SET_PIN
 PROXY_DATA_FILE=consts.PROXY_DATA_FILE
 VARIABLE_FILE=consts.VARIABLE_FILE
 BASE_FILE_PATH=consts.KOLLA_SOURCE_PATH
 DOCKER_OPTS= "--insecure-registry  "+docker_registry+":"+docker_port
 DOCKER_REGISTRY_IP=docker_registry+":"+docker_port
 list_network=[]
 list_storage=[]
 list_node=[]
 list_all=[]
 list_controller=[]
 list_compute=[]
 ip_control=None
 for key,value in host_name_map.iteritems():
      ip=value
      host_name=key
      logger.info('EXECUTING SET HOSTS PLAY')
      logger.info(playbook_path_sethosts)
      ret_hosts=ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_sethosts,
                {'target': ip,'host_name': host_name, 'PROXY_DATA_FILE': PROXY_DATA_FILE,
                 'VARIABLE_FILE': VARIABLE_FILE})
      if (ret_hosts!=0):
       logger.info("FAILED IN SETTING HOSTS FILE")
       exit(1)
      else:
       logger.info('SET HOSTNAME IN HOSTS')
      ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_sethostname,
      {'target': ip,'host_name': host_name, 'PROXY_DATA_FILE': PROXY_DATA_FILE,
       'VARIABLE_FILE': VARIABLE_FILE})
 for key,value in host_node_type_map.iteritems():
      ip=key
      node_type=value
      if(len(host_node_type_map)==1):
         list_all.append(ip)
         ip_control=ip
      if('compute' in node_type):
         list_compute.append(ip)
      if('controller' in node_type):
         list_controller.append(ip)
         ip_control=ip
      if('network' in node_type):
         list_network.append(ip)
      if('storage' in node_type):
         list_storage.append(ip)
      if('controller' not in node_type):
         list_node.append(ip)
 logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++')
 logger.info(list_all)
 logger.info(list_compute)
 logger.info(list_controller)
 logger.info(list_node)
 logger.info(list_storage)
 if ip_control in list_compute:
  check_var='present'
  logger.info('controller also a compute')
  logger.info(ip_control)
 else:
  check_var='absent'
  logger.info('controller not a compute')
 logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++')
 logger.info('SETUP KOLLA BASE PACKAGES')
 ret= ansible_playbook_launcher.__launch_ansible_playbook(iplist , playbook_path_set_kolla,
      {'target': docker_registry , 'DOCKER_OPTS' : DOCKER_OPTS ,
      'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP, 'kolla_base' : kolla_base ,
      'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE,
      'VARIABLE_FILE': VARIABLE_FILE, 'BASE_FILE_PATH':BASE_FILE_PATH, 'GIT_BRANCH':git_branch})
 logger.info(ret)
 print '#####################################################'
 if(ret!=0):
   logger.info ('FAILED IN SETTING KOLLA BASE PACKAGES')
   exit(1)

 if(operation is "deployregistry"):
    logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++')
    logger.info('SETUP REGISTRY:It will take bit time to setup your registry with comipled images')
    ret= ansible_playbook_launcher.__launch_ansible_playbook(iplist , playbook_path_set_registry,
                                  {'target': docker_registry , 'DOCKER_OPTS' : DOCKER_OPTS , 'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP,
                                   'kolla_base' : kolla_base , 'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE,
                                   'VARIABLE_FILE': VARIABLE_FILE, 'BASE_FILE_PATH':BASE_FILE_PATH})
    logger.info(ret)
    print '#####################################################'
    if(ret!=0):
       logger.info ('FAILED IN SETTING DOCKER REGISTRY')
       exit(1)
 ansible_playbook_launcher.__launch_ansible_playbook(iplist ,playbook_path_copy_key,
                          {'target': ip_control, 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE})
 for key_ip in iplist:
  	ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_push_key,{'target': key_ip ,'PROXY_DATA_FILE': PROXY_DATA_FILE,
                                                      'VARIABLE_FILE': VARIABLE_FILE})

 if not list_all:
 	logger.info('**********************MULTINODE_DEPLOYMENT******************************')
        ret_storage=None
        if list_storage:
           for storage_ip in list_storage:
            ret_storage= ansible_playbook_launcher.__launch_ansible_playbook(iplist,
                         playbook_path_launch_storage,{'target': storage_ip,
                         'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE,
                         'SECOND_STORAGE': second_storage, 'BASE_FILE_PATH':BASE_FILE_PATH, 'OPERATION': operation, 'BASE_SIZE': base_size, 'COUNT': count})

            if(ret_storage !=0):
                logger.info("FAILED IN SETTING STORAGE")
                exit(1)

        if git_branch.lower()=='stable/newton' :
         for node_ip in list_node:
           ret= ansible_playbook_launcher.__launch_ansible_playbook(iplist,
                playbook_path_launch_compute,{ 'DOCKER_OPTS' : DOCKER_OPTS ,
                'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP , 'target': node_ip,
                'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE,
                'BASE_FILE_PATH':BASE_FILE_PATH,'SECOND_STORAGE': second_storage, 'BASE_SIZE': base_size, 'COUNT': count, 'GIT_BRANCH':git_branch, 'DEFAULT': default,'VXLAN': vxlan})
           if(ret !=0):
              logger.info("FAILED IN COMPUTE")
              exit(1)
           else:
             logger.info("********************PLAYBOOK EXECUTED SUCCESSFULLY****************************")
        else:
         for node_ip in list_node:
            ret = ansible_playbook_launcher.__launch_ansible_playbook(iplist,
                 playbook_path_launch_compute_pike,{ 'DOCKER_OPTS' : DOCKER_OPTS ,
                 'DOCKER_REGISTRY_IP': DOCKER_REGISTRY_IP, 'target': node_ip,
                 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE,
                'BASE_FILE_PATH': BASE_FILE_PATH, 'SECOND_STORAGE': second_storage,'BASE_SIZE': base_size, 'COUNT': count, 'GIT_BRANCH':git_branch,'DEFAULT': default,'VXLAN': vxlan})

            if (ret != 0):
                print ret
                logger.info("FAILED IN COMPUTE PIKE")
                exit(1)
            else:
                logger.info("********************PLAYBOOK EXECUTED SUCCESSFULLY PIKE****************************")
           
        for controller_ip in list_controller:
          if len(list_storage)==1:
            ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_ceph_setup,{'target': controller_ip , 'VARIABLE_FILE': VARIABLE_FILE,'BASE_FILE_PATH':BASE_FILE_PATH})
          if git_branch.lower() == 'stable/newton':
           ret_controller=ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_launch_controller,{ 'target' : controller_ip , 'DOCKER_OPTS' : DOCKER_OPTS , 'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP , 'kolla_base' : kolla_base , 'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE ,'BASE_FILE_PATH':BASE_FILE_PATH,'EXT_SUB':ext_sub,'EXT_GW':ext_gw,'START_IP':ip_pool_start,'END_IP':ip_pool_end,'DEFAULT': default,'VXLAN': vxlan, 'GIT_BRANCH':git_branch})
           if (ret_controller !=0):
            logger.info("FAILED IN CONROLLER")
            exit(1)
          else:
           ret_controller=ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_launch_controller_pike,{ 'target' : controller_ip , 'DOCKER_OPTS' : DOCKER_OPTS , 'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP , 'kolla_base' : kolla_base , 'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE ,'BASE_FILE_PATH':BASE_FILE_PATH,'EXT_SUB':ext_sub,'EXT_GW':ext_gw,'START_IP':ip_pool_start,'END_IP':ip_pool_end,'DEFAULT': default,'VXLAN': vxlan, 'GIT_BRANCH':git_branch, 'CHECK_VAR':check_var})
           if (ret_controller !=0):
            logger.info("FAILED IN CONROLLER PIKE")
            print ret_controller
            exit(1)
        for node_ip in list_node:
           ret= ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_launch_iso_nw,{ 'target': node_ip,'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE, 'BASE_FILE_PATH':BASE_FILE_PATH})
           if(ret !=0):
              logger.error("NETWORK ADAPTATION FAILED IN COMPUTE")
              exit(1)
           else:
             logger.info("********************ISO NWK PLAYBOOK EXECUTED SUCCESSFULLY****************************")

        for node_ip in list_compute:
           vcpu_pin=hostCpuMap.get(node_ip)
           memory=reserve_memory.get(node_ip)
           ret= ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_launch_set_pin,{ 'target': node_ip,'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE, 'BASE_FILE_PATH':BASE_FILE_PATH, 'vcpu_pin': vcpu_pin, 'memory': memory, 'DEFAULT': default, 'VXLAN': vxlan})
           if(ret !=0):
              logger.error(" FAILED IN COMPUTE")
              exit(1)
           else:
             logger.info("******************** EXECUTED SUCCESSFULLY****************************")


 else:
        logger.info('ALL IN ONE DEPLOYEMENT')
        if git_branch.lower() == 'stable/newton':
         ret_all=ansible_playbook_launcher.__launch_ansible_playbook(list_all,playbook_path_launch_single_node,{ 'DOCKER_OPTS' : DOCKER_OPTS , 'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP , 'kolla_base' : kolla_base , 'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE,'BASE_FILE_PATH':BASE_FILE_PATH,'EXT_SUB':ext_sub,'EXT_GW':ext_gw,'START_IP':ip_pool_start,'END_IP':ip_pool_end,'SECOND_STORAGE': second_storage, 'BASE_SIZE': base_size, 'COUNT': count,'DEFAULT': default,'VXLAN': vxlan, 'GIT_BRANCH':git_branch})
         if (ret_all!=0):
           logger.info("FAILED IN DEPLOYMENT")
           exit(1)
         else:
           logger.info("SINGLE NODE COMPLETED")
        else:
          ret_all = ansible_playbook_launcher.__launch_ansible_playbook(list_all,playbook_path_launch_single_node_pike,{ 'DOCKER_OPTS' : DOCKER_OPTS , 'DOCKER_REGISTRY_IP' : DOCKER_REGISTRY_IP , 'kolla_base' : kolla_base , 'kolla_install' : kolla_install, 'PROXY_DATA_FILE': PROXY_DATA_FILE, 'VARIABLE_FILE': VARIABLE_FILE,'BASE_FILE_PATH':BASE_FILE_PATH,'EXT_SUB':ext_sub,'EXT_GW':ext_gw,'START_IP':ip_pool_start,'END_IP':ip_pool_end,'SECOND_STORAGE': second_storage, 'BASE_SIZE': base_size, 'COUNT': count,'DEFAULT': default, 'VXLAN': vxlan, 'GIT_BRANCH':git_branch})
          if (ret_all!=0):
           logger.info("FAILED IN DEPLOYMENT PIKE")
           print ret_all
           exit(1)
          else:
           logger.info("SINGLE NODE COMPLETED PIKE")
 logger.info("PROCESS COMPLETE")
