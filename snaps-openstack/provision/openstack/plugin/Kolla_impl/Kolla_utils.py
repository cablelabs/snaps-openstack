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

"""
Purpose : kolla Provisioning
Date :27/04/2017
Created By :Ashish
"""
import subprocess
import os
import sys
from common.utils import file_utils
from ansible_p.ansible_utils import ansible_configuration
import logging
import random
import shutil
from common.consts import consts
from collections import OrderedDict
logger = logging.getLogger('deploy_venv')
def main(config, operation):

 if config:
  logger.info("Validating configuration")
  #validation
  valid_config=__validate_configuration(config)
  if valid_config==False:
    logger.info('VALIDATION FAILED')
    exit(1)
  logger.info("Validation completed")
  __enable_key_ssh(config)
  iplist,host_type =__hostip_list(config)
  logger.info("***********************IP LIST**************************")
  logger.info(iplist)
  proxy_dic=__create_proxy_dic(config)
  logger.info("***********************PROXY****************************")
  logger.info(proxy_dic)
  credential_dic=__get_credentials(config)
  logger.info("***********************CREDENTIALS**********************")
  logger.info(credential_dic)
  git_branch=config.get(consts.OPENSTACK).get(consts.GIT_BRANCH)
  logger.info("***********************GIT BRANCH **********************")
  logger.info(git_branch)
  logger.info("*********************GLOBAL.YML*************************")
  __create_global(config, git_branch)
  hostname_map=__get_hostname_map(config)
  host_node_type_map= __create_host_nodetype_map(config)
  logger.info("**************MULTINODE INVENTORY FILE******************")
  __create_inventory_multinode(config,host_node_type_map)
  logger.info("**************DOCKER DAEMON JSON ***********************")
  __create_demon(config)

  logger.info("PROVISION_PREPARATION METHOD CALLED")
  deployment_type=config.get(consts.OPENSTACK ).get(consts.DEPLOYMENT_TYPE)

  ansible_configuration.provision_preparation(iplist, proxy_dic, git_branch, credential_dic, deployment_type,"False")
  docker_registry=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.REGISTRY)
  docker_port=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KOLLA_REGISTRY_PORT)
  kolla_base=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.BASE_DISTRIBUTION)
  kolla_install=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.INSTALL_TYPE)
  networks=config.get(consts.OPENSTACK).get("networks")
#  mtu_size=networks.get("mtu_size")
  default=networks.get("mtu_size").get("default")
  logger.info(default)
  vxlan=networks.get("mtu_size").get("vxlan")
  logger.info(vxlan)
  ext_sub=networks.get("external").get("subnet")
  logger.info(ext_sub)
  ext_gw=networks.get("external").get("gateway")
  logger.info(ext_gw)
  ip_pool_start=networks.get("external").get("ip_pool").get("start")
  logger.info(ip_pool_start)
  ip_pool_end=networks.get("external").get("ip_pool").get("end")
  logger.info(ip_pool_end)
  second_storage= config.get(consts.OPENSTACK ).get(consts.KOLLA).get("second_storage")
  logger.info(second_storage)
  base_size= config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.BASE_SIZE)
  logger.info(base_size)
  count= config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.COUNT)
  logger.info(count)
  hostsList=config.get(consts.OPENSTACK).get(consts.HOSTS)
  hostCpuMap={} # map to store cpus correponds to ip
  reserve_memory={}
  for host in hostsList:
    hostData = host.get('host')
    allInterface=hostData.get('interfaces')
    host_name=hostData.get('hostname')
    for interfaceData in allInterface:
     if interfaceData.get('type') == 'management':
       hostCpuMap[interfaceData.get('ip')] = hostData.get('isolcpus')
       reserve_memory[interfaceData.get('ip')] = hostData.get('reserved_host_memory_mb')

  ansible_configuration.launch_provisioning_kolla(iplist,git_branch,credential_dic,hostname_map,host_node_type_map,docker_registry,docker_port,kolla_base,kolla_install,ext_sub,ext_gw,ip_pool_start,ip_pool_end,second_storage, operation, hostCpuMap, reserve_memory,base_size,count,default,vxlan)
  BASE_FILE_PATH=consts.KOLLA_SOURCE_PATH
  FILES={"globals.yml","daemon.json","netvars.yml","inventory/multinode"}
  for i in FILES:
    os.remove(BASE_FILE_PATH+i)
    logger.info("deleted file "+i)
  logger.info("Successfully Done Everything")
 else:
  logger.info("Cannot read configuration")


def __get_credentials(config):
 credential_dic={}
 hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
 for i in range(len(hosts)):
  user=hosts[i].get(consts.HOST).get(consts.USER)
  password =hosts[i].get(consts.HOST).get(consts.PASSWORD)
  node_type=hosts[i].get(consts.HOST).get(consts.NODE_TYPE)
  credential_dic['user']=user
  credential_dic['password']=password
 return credential_dic



def __create_proxy_dic(config):
 logger.info("Creating Proxy dictionary")
 proxy_dic={}
 http_proxy=config.get(consts.OPENSTACK ).get(consts.PROXIES).get(consts.HTTP_PROXY)
 https_proxy=config.get(consts.OPENSTACK ).get(consts.PROXIES).get(consts.HTTPS_PROXY)
 ftp_proxy=config.get(consts.OPENSTACK ).get(consts.PROXIES).get(consts.FTP_PROXY)
 no_proxy=config.get(consts.OPENSTACK ).get(consts.PROXIES).get(consts.NO_PROXY)
 proxy_dic['http_proxy']="\""+http_proxy+"\""
 proxy_dic['https_proxy']="\""+https_proxy+"\""
 proxy_dic['ftp_proxy']="\""+ftp_proxy+"\""
 proxy_dic['no_proxy']="\""+no_proxy+"\""
 logger.info("Done with proxies")
 return proxy_dic

def __hostip_list(config):
 logger.info("Creating host ip list")
 hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
 list=[]
 host_node_map={}
 for i in range(len(hosts)):
    interfaces=hosts[i].get(consts.HOST).get(consts.INTERFACES)
    node_type=hosts[i].get(consts.HOST).get(consts.NODE_TYPE)
    hostname=hosts[i].get(consts.HOST).get(consts.HOSTNAME)
    host_ip=""
    host_node_map[hostname]=node_type
    for i in range(len(interfaces)):
      ip=interfaces[i].get(consts.IP)
      type=interfaces[i].get(consts.TYPE)
      if(type=="management") and ip:
       host_ip=ip
       list.append(host_ip)

 return list,host_node_map

def __get_hostname_map(config):
 if config:
  hostname_map={}
  hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
  for i in range(len(hosts)):
    interfaces=hosts[i].get(consts.HOST).get(consts.INTERFACES)
    hostname=hosts[i].get(consts.HOST).get('hostname')
    #node_type=hosts[i].get(consts.HOST).get(consts.NODE_TYPE)
    data_iface=""
    host_ip=""
    for i in range(len(interfaces)):
      ip=interfaces[i].get(consts.IP)
      type=interfaces[i].get(consts.TYPE)
      if(type=="management"):
       host_ip=ip
    hostname_map[hostname+`i`+`random.randint(111,999)`]=host_ip

    #if(node_type=="controller"):
    # hostname_map[node_type+`i`+`random.randint(111,999)`]=host_ip
    #elif(node_type=="compute"):
    # hostname_map[node_type+`i`+`random.randint(111,999)`]=host_ip
    #elif(node_type=="network"):
    # hostname_map[node_type+`i`+`random.randint(111,999)`]=host_ip
    #elif(node_type=="storage"):
    # hostname_map[node_type+`i`+`random.randint(111,999)`]=host_ip
    #elif(node_type=="all"):
    # hostname_map[node_type+`i`+`random.randint(111,999)`]=host_ip
 return hostname_map


def __create_demon(config):
  docker_registry=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.REGISTRY)
  docker_port=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KOLLA_REGISTRY_PORT)
  f_out = open(consts.DAEMON_FILE,"w")
  f_out.write("{ "+'"insecure-registries":["'+docker_registry+":"+docker_port+'"] }' )
  f_out.close()



def __create_global(config,git_branch):
 #basefile='/home/ubuntu/E2E/Aricent_IaaS/packages/source/globals_bak.yml'
 basefile=consts.GLOBAL_BASE_FILE
 f = open(basefile,'r')
 filedata=f.read()
 newfile=consts.GLOBAL_FILE

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.BASE_DISTRIBUTION)is not None):
  kolla_base_distro= config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.BASE_DISTRIBUTION)
  filedata=filedata.replace('#kolla_base_distro: "centos"','kolla_base_distro: "'+kolla_base_distro+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.INSTALL_TYPE) is not None):
  kolla_install_type= config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.INSTALL_TYPE)
  filedata=filedata.replace('#kolla_install_type: "binary"','kolla_install_type: "'+kolla_install_type+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KEEPALIVED_VIRTUAL_ROUTER_ID)is not None):
  virtual_router_id=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KEEPALIVED_VIRTUAL_ROUTER_ID)
  filedata=filedata.replace('#keepalived_virtual_router_id: "51"','keepalived_virtual_router_id: "'+virtual_router_id+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.INTERNAL_VIP_ADDRESS)is not None):
  internal_vip=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.INTERNAL_VIP_ADDRESS)
  filedata=filedata.replace('"10.10.10.254"','"'+internal_vip+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.EXTERNAL_VIP_ADDRESS)is not None):
  external_vip=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.EXTERNAL_VIP_ADDRESS)
  filedata=filedata.replace('#kolla_external_vip_address:','kolla_external_vip_address: '+'"'+external_vip+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.EXTERNAL_INTERFACE)is not None):
  external_interface=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.EXTERNAL_INTERFACE)
  filedata=filedata.replace('#kolla_external_vip_interface:','kolla_external_vip_interface: '+'"'+external_interface+'"')

 if(config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.REGISTRY)is not None):
  docker_registry=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.REGISTRY)
  docker_port=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KOLLA_REGISTRY_PORT)
  filedata=filedata.replace('#docker_registry: "172.16.0.10:4000"','docker_registry: "'+docker_registry+':'+docker_port+'"')
 #filedata=filedata.replace('#enable_cinder: "no"','enable_cinder: "yes"')

 if (config.get(consts.OPENSTACK ).get(consts.SERVICES)is not None):
  service_str=config.get(consts.OPENSTACK ).get(consts.SERVICES)
  #service_list=service_str.split(",")

  for services in service_str :
     logger.info("###############"+services+"##################")
     filedata=filedata.replace('#enable_cinder: "no"','enable_cinder: "no"')
     if (services == 'cinder'):
      if ('ceph' in service_str):
         filedata=filedata.replace('enable_ceph: "no"','enable_ceph: "yes"')
         filedata=filedata.replace('#enable_ceph_rgw: "no"','enable_ceph_rgw: "yes"')
         filedata=filedata.replace('#glance_backend_ceph: "no"','glance_backend_ceph: "yes"')
         filedata=filedata.replace('#glance_backend_file: "yes"','glance_backend_file: "no"')
         filedata=filedata.replace('enable_cinder: "no"','enable_cinder: "yes"')
         filedata=filedata.replace('#cinder_backend_ceph: "{{ enable_ceph }}"','cinder_backend_ceph: "{{ enable_ceph }}"')
      else:
         filedata=filedata.replace('enable_cinder: "no"','enable_cinder: "yes"')
         filedata=filedata.replace('enable_ceph: "no"','enable_ceph: "no"')
         if git_branch.lower() == 'stable/newton':
          filedata=filedata.replace('#enable_cinder_backend_iscsi: "no"','enable_cinder_backend_iscsi: "yes"')
         elif git_branch.lower() == 'stable/pike':
          filedata = filedata.replace('#enable_cinder_backend_iscsi: "no"','enable_cinder_backend_iscsi: "no"')
         filedata=filedata.replace('#enable_cinder_backend_lvm: "no"','enable_cinder_backend_lvm: "yes"')
         filedata=filedata.replace('#cinder_backend_ceph: "{{ enable_ceph }}"','cinder_backend_ceph: "{{ enable_ceph }}"')
         filedata=filedata.replace('#cinder_volume_group: "cinder-volumes"','cinder_volume_group: "cinder-volumes"')
     if (services == 'magnum'):
       filedata=filedata.replace('enable_magnum: "no"','enable_magnum: "yes"')
       if git_branch.lower() == 'stable/newton':
        filedata=filedata.replace('#enable_barbican: "no"','enable_barbican: "yes"')
     if (services== 'ceilometer'):
       filedata=filedata.replace('#enable_ceilometer: "no"','enable_ceilometer: "yes"')
       if git_branch.lower() == 'stable/newton':
        filedata=filedata.replace('#enable_mongodb: "no"','enable_mongodb: "yes"')
       else:
        filedata = filedata.replace('#enable_gnocchi: "no"', 'enable_gnocchi: "yes"')
     if (services== 'tempest'):
        filedata=filedata.replace('#enable_tempest: "no"','enable_tempest: "yes"')
     if (services == 'tacker'):
         filedata = filedata.replace('#enable_tacker: "no"', 'enable_tacker: "yes"')
         filedata = filedata.replace('#enable_mistral: "no"', 'enable_mistral: "yes"')
         filedata = filedata.replace('#enable_redis: "no"', 'enable_redis: "yes"')
         filedata = filedata.replace('#enable_barbican: "no"', 'enable_barbican: "yes"')
 proxy_http=config.get(consts.OPENSTACK).get('proxies').get('http_proxy')
 proxy_https=config.get(consts.OPENSTACK).get('proxies').get('https_proxy')
 filedata=filedata.replace('#docker_registry_password: "correcthorsebatterystaple"','#docker_registry_password: "correcthorsebatterystaple" \ncontainer_proxy: \n  http_proxy: "'+proxy_http+'"\n  https_proxy: "'+proxy_https+'"\n  no_proxy: "localhost,127.0.0.1,{{ kolla_internal_vip_address }},{{ api_interface_address }}"')
 docker_registry=None
 hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
 gateway=""
 for i in range(len(hosts)):
    interfaces=hosts[i].get(consts.HOST).get(consts.INTERFACES)
    node_type=hosts[i].get(consts.HOST).get(consts.NODE_TYPE)
    if('controller' in node_type or len(hosts)==1):
     data_iface=""
     host_ip=""
     for i in range(len(interfaces)):
       test_ip=interfaces[i].get(consts.IP)
       name=interfaces[i].get(consts.NAME)
       name=name.lower()
       type=interfaces[i].get(consts.TYPE)
       type = type.lower()
       if(type=="management"):
        filedata=filedata.replace('#network_interface: "eth0"','network_interface: "'+name+'"')

       elif(type=="data"):
         filedata=filedata.replace('#neutron_external_interface: "eth1"','neutron_external_interface: "'+name+'"')
         gateway=interfaces[i].get("gateway")
       elif(type=="tenant"):
         filedata=filedata.replace('#tunnel_interface: "{{ network_interface }}"','tunnel_interface: "'+name+'"')
       else:
         logger.error("Incorrect interface type")
         exit(1)


 f.close()
 shutil.copy2(basefile,newfile)

 file_path=consts.NETVAR_FILE
 with open(file_path, "w") as text_file:
      text_file.write("--- ")
      text_file.write("\n")
      text_file.write("external_gw: "+ gateway)
      text_file.write("\n")
 f = open(newfile,'w')
 f.write(filedata)
 f.close()

def __create_host_nodetype_map(config):
 if config:
  hostnode_map={}
  hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
  for i in range(len(hosts)):
    interfaces=hosts[i].get(consts.HOST).get(consts.INTERFACES)
    node_type=hosts[i].get(consts.HOST).get(consts.NODE_TYPE)

    data_iface=""
    host_ip=""
    for i in range(len(interfaces)):
      ip=interfaces[i].get(consts.IP)
      type=interfaces[i].get(consts.TYPE)
      if(type=="management"):
       host_ip=ip
    hostnode_map[host_ip]=node_type
 return hostnode_map




def __create_inventory_multinode(config,host_node_type_map):
 basefile=consts.INVENTORY_MULTINODE_BASE_FILE
 f = open(basefile,'r')
 filedata=f.read()
 f.close()
 newfile=consts.INVENTORY_MULTINODE_FILE
 for key,value in host_node_type_map.iteritems():
  if('network' in value):
   filedata=filedata.replace('[network]','[network] \n'+key)
  if('storage' in value):
   filedata=filedata.replace('[storage]','[storage] \n'+key)
  if ('controller' in value):
   filedata=filedata.replace('[control]','[control] \n'+key)
  if ('compute' in value):
   filedata=filedata.replace('[compute]','[compute] \n'+key)
  if ('monitoring' in value):
   filedata=filedata.replace('[monitoring]','[monitoring] \n'+key)
 shutil.copy2(basefile,newfile)
 f = open(newfile,'w')
 f.write(filedata)
 f.close()

def __validate_configuration(config):
 """
 This method is responsible for validating the information in input configuration file
 :param config : input configuration file
 :return : none or list of the ips
 """
 valid=True
 config_dict = config.get(consts.OPENSTACK)
 logger.debug("Starting validation")
 ip_list = []
 # Check if git_branch is defined
 if config_dict.get(consts.GIT_BRANCH)==None:
   logger.error("Value of git_branch not present")
   valid=False
 # Check if proxy values present
 proxy_dict = config_dict.get(consts.PROXIES)
 logger.info("======Your proxy settings for Cloud host machines are:======")
 logger.info(proxy_dict)

 #Check if  interfaces defined for each host
 hosts_list = config_dict.get(consts.HOSTS)
 check_service_host = False
 logger.debug(hosts_list)
 for host in hosts_list:
  logger.debug("**********HOST INFORMATION************")
  logger.debug(host)
  host_dict = host.get(consts.HOST)
  for key,value in host_dict.iteritems():
    if key=="interfaces":
     if len(value) < 2:
      logger.error("Each host must have two interfaces")
      valid=False
     # Iterating through interface information
     for interfaces in value:
      logger.debug(interfaces.get(consts.TYPE))
      if interfaces.get(consts.IP)==None and interfaces.get(consts.TYPE)=="management":
       logger.error("Ip must be defined for interface type:management")
       valid=False

      elif interfaces.get(consts.TYPE).lower() !="management" and \
           interfaces.get(consts.TYPE).lower() !="data" and \
           interfaces.get(consts.TYPE).lower() !="tenant":
       logger.error("Invalid interface type")
       valid=False

      elif interfaces.get(consts.NAME)==None:
       logger.error("Interface name must be defined")
       valid=False
      #elif interfaces.get(consts.MAC)==None:
      # logger.error("Interface mac must be defined")
      # valid=False
      #elif interfaces.get(consts.IP)!=None and interfaces.get(consts.TYPE)=="management" and interfaces.get(consts.GATEWAY)==None:
      #logger.error('Gateway must be defined for interface type management')
      #valid=False
      elif interfaces.get(consts.IP)!=None and interfaces.get(consts.TYPE)=="management":
       ip_list.append(interfaces.get('ip'))

    # Checking for other parameters in each host
    elif key=="hostname" and value==None:
     logger.error("Hostname must be defined")
     valid=False
    elif key=="password" and value==None:
     logger.error("password must be defined")
     valid=False
    #elif key=="node_type":
     #if not (value=="controller" or value=="compute" or value=="all" or value=="network" or value=="volume") :
      #valid=False
      #logger.error("Node type must be \"controller\"  \"compute\" \"all\"")

     logger.debug(value)

    elif key=="user":
     if value==None:
      logger.error("User must be defined")
      valid=False

 if (config_dict.get(consts.KOLLA).get(consts.BASE_DISTRIBUTION)==None):
   logger.info("KOLLA_BASE_DISTRO CANNOT BE NULL")
   valid=False
 if((config_dict.get(consts.KOLLA).get(consts.BASE_DISTRIBUTION) == 'ubuntu') or (config_dict.get(consts.KOLLA).get(consts.BASE_DISTRIBUTION) == 'centos')):
    logger.info("VALID CONFIG")
 else:
    logger.info("NOT A VALID OPTION")
    valid=False
 if (config_dict.get(consts.KOLLA).get(consts.INSTALL_TYPE)==None):
   logger.info("KOLLA_INSTALL_TYPE CANNOT BE NULL")
   valid=False
 if((config_dict.get(consts.KOLLA).get(consts.INSTALL_TYPE) == 'source') or (config_dict.get(consts.KOLLA).get(consts.INSTALL_TYPE) == 'binary')):
   logger.info("VALID CONFIG")
 else:
   logger.info("NOT A VALID OPTION")
   valid=False
 if (config_dict.get(consts.KOLLA).get(consts.KEEPALIVED_VIRTUAL_ROUTER_ID)==None):
   logger.info("VIRTUAL_ROUTER_ID CANNOT BE NULL")
   valid=False
 if (config_dict.get(consts.KOLLA).get(consts.INTERNAL_VIP_ADDRESS)==None):
   logger.info("KOLLA_INTERNAL_VIP CANNOT BE NULL")
   valid=False
 if (config_dict.get(consts.KOLLA).get(consts.REGISTRY)==None):
   logger.info("KOLLA_REGISTRY CANNOT BE NULL")
   valid=False
 if (config.get(consts.OPENSTACK ).get(consts.KOLLA).get("second_storage")is None and "ceph" in config.get(consts.OPENSTACK ).get(consts.SERVICES)):
   logger.info("SECOND STORAGE IS NOT DEFINED WHILE USING CEPH")
   valid=False
 if valid:
  return ip_list
 else:
  exit(1)


def __enable_key_ssh(config):
 command="sed -i '/host_key_checking/c\#host_key_checking = False' " + consts.ANSIBLE_CONF
 subprocess.call(command ,shell=True)
 command_time="sed -i '/#timeout = 10/c\\timeout = 50' " + consts.ANSIBLE_CONF
 subprocess.call(command_time ,shell=True)
 hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
 for i in range(len(hosts)):
    user_name=hosts[i].get(consts.HOST).get(consts.USER)
    if user_name!='root':
       logger.info('USER MUST BE ROOT')
       exit(0)
    password=hosts[i].get(consts.HOST).get(consts.PASSWORD)
    interfaces=hosts[i].get(consts.HOST).get(consts.INTERFACES)
    host_ip=""
    check_dir=os.path.isdir(consts.SSH_PATH)
    if not check_dir:
      os.makedirs(consts.SSH_PATH)
    for i in range(len(interfaces)):
      ip=interfaces[i].get(consts.IP)
      type=interfaces[i].get(consts.TYPE)
      if(type=="management"):
       host_ip=ip
       logger.info('GENERATING SSH KEY')
       subprocess.call('echo -e y|ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""', shell=True)
       logger.info('PUSHING KEY TO HOSTS')
       command= "sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s" %(password,user_name,host_ip)
       res=subprocess.call(command,shell=True)
       if(res!=0):
        logger.info('ERROR IN PUSHING KEY:Probaly the key is already present in remote host')
        #exit(1)
       logger.info('SSH KEY BASED AUTH ENABLED')
 return True

def clean_up(config, operation):
  """
  This method is used for cleanup of openstack services
  :param config :input configuration file
  :return ret :t/f
  """

  if config:
    logger.info("Validating configuration")
  #validation
  list_ip,host_type = __hostip_list(config)
  docker_registry=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.REGISTRY)
  docker_port=config.get(consts.OPENSTACK ).get(consts.KOLLA).get(consts.KOLLA_REGISTRY_PORT)
  second_storage= config.get(consts.OPENSTACK ).get(consts.KOLLA).get("second_storage")
  git_branch=config.get(consts.OPENSTACK).get(consts.GIT_BRANCH)
  if list_ip is None:
    logger.info("Not valid configurations")
    exit(1)
  else:
   logger.debug("***********************CREDENTIALS**********************")
   logger.debug(list_ip)
   service_list=_getservice_list(config)
   logger.info(service_list)
   ret = ansible_configuration.clean_up_kolla(list_ip,git_branch,docker_registry,docker_port,service_list, operation, second_storage)
   return ret

def _getservice_list(config):
 service_str=["Empty"]
 if (config.get(consts.OPENSTACK ).get(consts.SERVICES)is not None):
  service_str=config.get(consts.OPENSTACK ).get(consts.SERVICES)
 return service_str
