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
import logging
import random
import shutil
import subprocess

import os

from snaps_openstack.ansible_p.ansible_utils import ansible_configuration
from snaps_openstack.common.consts import consts

logger = logging.getLogger('deploy_venv')


# TODO/FIXME - rename and break apart function
def main(config, operation):
    if config:
        logger.info("Validating configuration")
        # validation
        valid_config = __validate_configuration(config)
        if valid_config is False:
            logger.info('VALIDATION FAILED')
            exit(1)
        logger.info("Validation completed")
        __enable_key_ssh(config)
        iplist, host_type = __hostip_list(config)
        logger.info("***********************IP LIST**************************")
        logger.info(iplist)
        proxy_dic = __create_proxy_dic(config)
        logger.info("***********************PROXY****************************")
        logger.info(proxy_dic)
        credential_dic = __get_credentials(config)
        logger.info("***********************CREDENTIALS**********************")
        logger.info(credential_dic)
        git_branch = config.get(consts.OPENSTACK).get(consts.GIT_BRANCH)
        logger.info("***********************GIT BRANCH **********************")
        logger.info(git_branch)
        kolla_tag = config.get(consts.OPENSTACK).get(consts.KOLLA_TAG)
        logger.info("***********************KOLLA TAG **********************")
        logger.info(kolla_tag)
        kolla_ansible_tag = config.get(consts.OPENSTACK).get(
            consts.KOLLA_ANSIBLE_TAG)
        logger.info(
            "***********************KOLLA-ANSIBLE TAG **********************")
        logger.info(kolla_ansible_tag)
        logger.info("*********************GLOBAL.YML*************************")
        if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
                consts.PULL_HUB) is not None):
            pull_from_hub = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
                consts.PULL_HUB)
            if pull_from_hub != "yes":
                pull_from_hub = "no"
        else:
            pull_from_hub = "no"
        __create_global(config, git_branch, pull_from_hub)
        hostname_map = __get_hostname_map(config)
        host_node_type_map = __create_host_nodetype_map(config)
        host_storage_node_map = __create_host_storage_node_map(config, host_node_type_map)
        logger.info(host_storage_node_map)
        host_sriov_interface_node_map = __create_host_sriov_interface_node_map(config)
        logger.info(host_sriov_interface_node_map)

        logger.info("**************MULTINODE INVENTORY FILE******************")
        __create_inventory_multinode(host_node_type_map)
        logger.info("**************DOCKER DAEMON JSON ***********************")
        if pull_from_hub != "yes":
            __create_daemon(config)

        logger.info("PROVISION_PREPARATION METHOD CALLED")

        ansible_configuration.provision_preparation(proxy_dic, credential_dic)
        docker_registry = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.REGISTRY)
        docker_port = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.KOLLA_REGISTRY_PORT)
        kolla_base = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.BASE_DISTRIBUTION)
        kolla_install = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.INSTALL_TYPE)
        networks = config.get(consts.OPENSTACK).get("networks")
        default = networks.get("mtu_size").get("default")
        logger.info(default)
        vxlan = networks.get("mtu_size").get("vxlan")
        logger.info(vxlan)
        ext_sub = networks.get("external").get("subnet")
        logger.info(ext_sub)
        ext_gw = networks.get("external").get("gateway")
        logger.info(ext_gw)
        ip_pool_start = networks.get("external").get("ip_pool").get("start")
        logger.info(ip_pool_start)
        ip_pool_end = networks.get("external").get("ip_pool").get("end")
        logger.info(ip_pool_end)
        dpdk_enable=None
        service_list = config.get(consts.OPENSTACK).get(consts.SERVICES)
        if 'dpdk' in service_list:
           dpdk_enable="yes"
        logger.info(dpdk_enable)
        base_size = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.BASE_SIZE)
        logger.info(base_size)
        count = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.COUNT)
        logger.info(count)
        hosts_list = config.get(consts.OPENSTACK).get(consts.HOSTS)
        host_cpu_map = {}  # map to store cpus correponds to ip
        reserve_memory = {}
        for host in hosts_list:
            host_data = host.get('host')
            all_interface = host_data.get('interfaces')
            for interfaceData in all_interface:
                if interfaceData.get('type') == 'management':
                    host_cpu_map[interfaceData.get('ip')] = host_data.get(
                        'isolcpus')
                    reserve_memory[interfaceData.get('ip')] = host_data.get(
                        'reserved_host_memory_mb')

        ansible_configuration.launch_provisioning_kolla(
            iplist, git_branch, kolla_tag, kolla_ansible_tag, hostname_map,
            host_node_type_map, docker_registry, docker_port, kolla_base,
            kolla_install, ext_sub, ext_gw, ip_pool_start, ip_pool_end,
            operation, host_cpu_map, reserve_memory, base_size,
            count, default, vxlan, pull_from_hub, host_storage_node_map, host_sriov_interface_node_map,
			dpdk_enable)
        base_file_path = consts.KOLLA_SOURCE_PATH
        files = {"globals.yml", "daemon.json", "netvars.yml",
                 "inventory/multinode"}
        for i in files:
            try:
                os.remove(base_file_path + i)
            except OSError:
                logger.info("FILE MUST HAVE BEEN REMOVED")
            logger.info("deleted file " + i)
        logger.info("Successfully Done Everything")
    else:
        logger.info("Cannot read configuration")

def __create_host_storage_node_map(config, host_node_type_map):
 if config:
  host_storage_node_map={}
  hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
  host_ip=""

  for key,value in host_node_type_map.iteritems():
    if('storage' in value or 'all' in value):
      host_ip=key;
      for j in range(len(hosts)):
        interfaces=hosts[j].get(consts.HOST).get(consts.INTERFACES)
        node_type=hosts[j].get(consts.HOST).get(consts.NODE_TYPE)
        second_storage=hosts[j].get(consts.HOST).get(consts.SECOND_STORAGE)
        for i in range(len(interfaces)):
          ip=interfaces[i].get(consts.IP)
          if ip is host_ip:
            host_storage_node_map[host_ip]=second_storage

 return host_storage_node_map 

def __create_host_sriov_interface_node_map(config):
 if config:
  host_sriov_interface_node_map={}
  hosts=config.get(consts.OPENSTACK).get(consts.HOSTS)
  for j in range(len(hosts)):
    interfaces=hosts[j].get(consts.HOST).get(consts.INTERFACES)
    sriov_interface=hosts[j].get(consts.HOST).get(consts.SRIOV_INTERFACE)
    logger.info(sriov_interface)
    for i in range(len(interfaces)):
      ip=interfaces[i].get(consts.IP)
      iface_type = interfaces[i].get(consts.TYPE)
      if(iface_type=="management") and ip :
        host_sriov_interface_node_map[ip]=sriov_interface
 
 return host_sriov_interface_node_map

def __get_credentials(config):
    credential_dic = {}
    hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)
    for i in range(len(hosts)):
        user = hosts[i].get(consts.HOST).get(consts.USER)
        password = hosts[i].get(consts.HOST).get(consts.PASSWORD)
        credential_dic['user'] = user
        credential_dic['password'] = password
    return credential_dic


def __create_proxy_dic(config):
    logger.info("Creating Proxy dictionary")
    proxy_dic = {}
    http_proxy = config.get(consts.OPENSTACK).get(consts.PROXIES).get(
        consts.HTTP_PROXY)
    https_proxy = config.get(consts.OPENSTACK).get(consts.PROXIES).get(
        consts.HTTPS_PROXY)
    ftp_proxy = config.get(consts.OPENSTACK).get(consts.PROXIES).get(
        consts.FTP_PROXY)
    no_proxy = config.get(consts.OPENSTACK).get(consts.PROXIES).get(
        consts.NO_PROXY)
    proxy_dic['http_proxy'] = "\"" + http_proxy + "\""
    proxy_dic['https_proxy'] = "\"" + https_proxy + "\""
    proxy_dic['ftp_proxy'] = "\"" + ftp_proxy + "\""
    proxy_dic['no_proxy'] = "\"" + no_proxy + "\""
    logger.info("Done with proxies")
    return proxy_dic


def __hostip_list(config):
    logger.info("Creating host ip list")
    hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)
    out_list = []
    host_node_map = {}

    for j in range(len(hosts)):
        interfaces = hosts[j].get(consts.HOST).get(consts.INTERFACES)
        node_type = hosts[j].get(consts.HOST).get(consts.NODE_TYPE)
        hostname = hosts[j].get(consts.HOST).get(consts.HOSTNAME)
        host_node_map[hostname] = node_type
        for i in range(len(interfaces)):
            ip = interfaces[i].get(consts.IP)
            iface_type = interfaces[i].get(consts.TYPE)
            if (iface_type == "management") and ip:
                host_ip = ip
                out_list.append(host_ip)

    return out_list, host_node_map


def __get_hostname_map(config):
    if config:
        hostname_map = {}
        hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)

        for j in range(len(hosts)):
            interfaces = hosts[j].get(consts.HOST).get(consts.INTERFACES)
            hostname = hosts[j].get(consts.HOST).get('hostname')
            host_ip = ""
            for i in range(len(interfaces)):
                ip = interfaces[i].get(consts.IP)
                iface_type = interfaces[i].get(consts.TYPE)
                if (iface_type == "management"):
                    host_ip = ip
            hostname_map[hostname + `i` + `random.randint(111, 999)`] = host_ip
        return hostname_map


def __create_daemon(config):
    docker_registry = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
        consts.REGISTRY)
    docker_port = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
        consts.KOLLA_REGISTRY_PORT)
    f_out = open(consts.DAEMON_FILE, "w")
    f_out.write(
        "{ " + '"insecure-registries":["' + docker_registry + ":" + str(
            docker_port) + '"] }')
    f_out.close()


def __create_global(config, git_branch, pull_from_hub):
    basefile = consts.GLOBAL_BASE_FILE
    f = open(basefile, 'r')
    filedata = f.read()
    newfile = consts.GLOBAL_FILE
    if pull_from_hub == "yes":
        release_value = git_branch.split('stable/')
        filedata = filedata.replace(
            '#openstack_release: "auto"',
            'openstack_release: "' + release_value[1] + '"')
    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.BASE_DISTRIBUTION) is not None):
        kolla_base_distro = config.get(
            consts.OPENSTACK).get(consts.KOLLA).get(consts.BASE_DISTRIBUTION)
        filedata = filedata.replace(
            '#kolla_base_distro: "centos"',
            'kolla_base_distro: "' + kolla_base_distro + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.INSTALL_TYPE) is not None):
        kolla_install_type = config.get(consts.OPENSTACK).get(
            consts.KOLLA).get(consts.INSTALL_TYPE)
        filedata = filedata.replace(
            '#kolla_install_type: "binary"',
            'kolla_install_type: "' + kolla_install_type + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.KEEPALIVED_VIRTUAL_ROUTER_ID) is not None):
        virtual_router_id = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.KEEPALIVED_VIRTUAL_ROUTER_ID)
        filedata = filedata.replace(
            '#keepalived_virtual_router_id: "51"',
            'keepalived_virtual_router_id: "' + virtual_router_id + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.INTERNAL_VIP_ADDRESS) is not None):
        internal_vip = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.INTERNAL_VIP_ADDRESS)
        filedata = filedata.replace('"10.10.10.254"', '"' + internal_vip + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.EXTERNAL_VIP_ADDRESS) is not None):
        external_vip = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.EXTERNAL_VIP_ADDRESS)
        filedata = filedata.replace(
            '#kolla_external_vip_address:',
            'kolla_external_vip_address: ' + '"' + external_vip + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.EXTERNAL_INTERFACE) is not None):
        external_interface = config.get(consts.OPENSTACK).get(
            consts.KOLLA).get(consts.EXTERNAL_INTERFACE)
        filedata = filedata.replace(
            '#kolla_external_vip_interface:',
            'kolla_external_vip_interface: ' + '"' + external_interface + '"')

    if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.REGISTRY) is not None):
        docker_registry = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.REGISTRY)
        docker_port = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
            consts.KOLLA_REGISTRY_PORT)
        if pull_from_hub != "yes":
            filedata = filedata.replace(
                '#docker_registry: "172.16.0.10:4000"',
                'docker_registry: "' + docker_registry + ':' + str(
                    docker_port) + '"')
        elif (config.get(consts.OPENSTACK).get(consts.KOLLA).get(consts.DOCKER_NAMESPACE) is not None):
            if config.get(consts.OPENSTACK).get(consts.KOLLA).get(consts.DOCKER_NAMESPACE) is not '':
                docker_namespace = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
                    consts.DOCKER_NAMESPACE)
                logger.info("Using docker_namespace " + docker_namespace)
                filedata = filedata.replace(
                    '#docker_namespace: "companyname"',
                    'docker_namespace: "' + docker_namespace +'"')

    proxy_http = config.get(consts.OPENSTACK).get('proxies').get('http_proxy')
    proxy_https = config.get(consts.OPENSTACK).get('proxies').get(
        'https_proxy')
    filedata = filedata.replace(
        '#docker_registry_password: "correcthorsebatterystaple"',
        '#docker_registry_password: "correcthorsebatterystaple" \ncontainer_proxy: \n  http_proxy: "'
        + proxy_http + '"\n  https_proxy: "' + proxy_https
        + '"\n  no_proxy: "localhost,127.0.0.1,{{ kolla_internal_vip_address }},{{ api_interface_address }}"')


    if config.get(consts.OPENSTACK).get(consts.SERVICES) is not None:
        service_str = config.get(consts.OPENSTACK).get(consts.SERVICES)

        for services in service_str:
            logger.info("###############" + services + "##################")
            filedata = filedata.replace('#enable_cinder: "no"',
                                        'enable_cinder: "no"')
            if services == 'cinder':
                if 'ceph' in service_str:
                    filedata = filedata.replace('enable_ceph: "no"',
                                                'enable_ceph: "yes"')
                    filedata = filedata.replace('#enable_ceph_rgw: "no"',
                                                'enable_ceph_rgw: "yes"')
                    filedata = filedata.replace('#glance_backend_ceph: "no"',
                                                'glance_backend_ceph: "yes"')
                    filedata = filedata.replace('#glance_backend_file: "yes"',
                                                'glance_backend_file: "no"')
                    filedata = filedata.replace('enable_cinder: "no"',
                                                'enable_cinder: "yes"')
                    filedata = filedata.replace(
                        '#cinder_backend_ceph: "{{ enable_ceph }}"',
                        'cinder_backend_ceph: "{{ enable_ceph }}"')
                else:
                    filedata = filedata.replace('enable_cinder: "no"',
                                                'enable_cinder: "yes"')
                    filedata = filedata.replace('enable_ceph: "no"',
                                                'enable_ceph: "no"')
                    filedata = filedata.replace(
                        '#enable_cinder_backend_iscsi: "no"',
                        'enable_cinder_backend_iscsi: "no"')

                    filedata = filedata.replace(
                        '#enable_cinder_backend_lvm: "no"',
                        'enable_cinder_backend_lvm: "yes"')
                    filedata = filedata.replace(
                        '#cinder_backend_ceph: "{{ enable_ceph }}"',
                        'cinder_backend_ceph: "{{ enable_ceph }}"')
                    filedata = filedata.replace(
                        '#cinder_volume_group: "cinder-volumes"',
                        'cinder_volume_group: "cinder-volumes"')
            if services == 'magnum':
                filedata = filedata.replace('enable_magnum: "no"',
                                            'enable_magnum: "yes"')
            if services == 'designate':
                filedata = filedata.replace('#enable_designate: "no"',
                                            'enable_designate: "yes"')
                filedata = filedata.replace('#enable_horizon_designate: "{{ enable_designate | bool }}"',
                                            'enable_horizon_designate: "{{ enable_designate | bool }}"')

            if services == 'ceilometer':
                filedata = filedata.replace('#enable_ceilometer: "no"',
                                            'enable_ceilometer: "yes"')
                filedata = filedata.replace('#enable_gnocchi: "no"',
                                            'enable_gnocchi: "yes"')
            if services == 'tempest':
                filedata = filedata.replace('#enable_tempest: "no"',
                                            'enable_tempest: "yes"')
            if services == 'tacker':
                filedata = filedata.replace('#enable_tacker: "no"',
                                            'enable_tacker: "yes"')
                filedata = filedata.replace('#enable_mistral: "no"',
                                            'enable_mistral: "yes"')
                filedata = filedata.replace('#enable_redis: "no"',
                                            'enable_redis: "yes"')
                filedata = filedata.replace('#enable_barbican: "no"',
                                            'enable_barbican: "yes"')
            
            if services == 'sriov':
                filedata = filedata.replace('enable_neutron_sriov: "no"',
                                             'enable_neutron_sriov: "yes"')
            if services == 'dpdk':
                filedata = filedata.replace('#ovs_datapath: "netdev"',
                                            'ovs_datapath: "netdev"')
                filedata = filedata.replace('enable_ovs_dpdk: "no"',
                                            'enable_ovs_dpdk: "yes"')
                filedata = filedata.replace('#enable_openvswitch: "{{ neutron_plugin_agent != \'linuxbridge\' }}"',
                                            'enable_openvswitch: "yes"')
                filedata = filedata.replace('#tunnel_interface: "{{ network_interface }}"',
                                            'tunnel_interface: "dpdk_bridge"')
                filedata = filedata.replace('#neutron_bridge_name: "dpdk_bridge"',
                                            'neutron_bridge_name: "dpdk_bridge"')
                if (config.get(consts.OPENSTACK).get(consts.KOLLA).get(consts.EXTERNAL_INTERFACE) is not None):
                   external_interface = config.get(consts.OPENSTACK).get(consts.KOLLA).get(consts.EXTERNAL_INTERFACE)
                   filedata = filedata.replace('kolla_external_vip_interface: '+'"'+external_interface+'"',
                                            'kolla_external_vip_interface: "dpdk_bridge"')

    hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)
    gateway = ""
    netmask = ""
    
    for j in range(len(hosts)):
        interfaces = hosts[j].get(consts.HOST).get(consts.INTERFACES)
        node_type = hosts[j].get(consts.HOST).get(consts.NODE_TYPE)
        if 'controller' in node_type or len(hosts) == 1:
            for i in range(len(interfaces)):
                name = interfaces[i].get(consts.NAME)
                name = name.lower()
                iface_type = interfaces[i].get(consts.TYPE)
                iface_type = iface_type.lower()
                if iface_type == "management":
                    filedata = filedata.replace(
                        '#network_interface: "eth0"',
                        'network_interface: "' + name + '"')

                elif iface_type == "data":
                    filedata = filedata.replace(
                        '#neutron_external_interface: "eth1"',
                        'neutron_external_interface: "' + name + '"')
                    gateway = interfaces[i].get("gateway")
                elif iface_type == "tenant":
                    filedata = filedata.replace(
                        '#tunnel_interface: "{{ network_interface }}"',
                        'tunnel_interface: "' + name + '"')
                else:
                    logger.error("Incorrect interface type")
                    exit(1)

    f.close()
    shutil.copy2(basefile, newfile)

    file_path = consts.NETVAR_FILE
    with open(file_path, "w") as text_file:
        text_file.write("--- ")
        text_file.write("\n")
        text_file.write("external_gw: " + gateway)
        text_file.write("\n")
    f = open(newfile, 'w')
    f.write(filedata)
    f.close()


def __create_host_nodetype_map(config):
    if config:
        hostnode_map = {}
        hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)

        for j in range(len(hosts)):
            interfaces = hosts[j].get(consts.HOST).get(consts.INTERFACES)
            node_type = hosts[j].get(consts.HOST).get(consts.NODE_TYPE)

            host_ip = ""
            for i in range(len(interfaces)):
                ip = interfaces[i].get(consts.IP)
                iface_type = interfaces[i].get(consts.TYPE)
                if iface_type == "management":
                    host_ip = ip
            hostnode_map[host_ip] = node_type
        return hostnode_map


def __create_inventory_multinode(host_node_type_map):
    basefile = consts.INVENTORY_MULTINODE_BASE_FILE
    f = open(basefile, 'r')
    filedata = f.read()
    f.close()
    newfile = consts.INVENTORY_MULTINODE_FILE
    for key, value in host_node_type_map.items():
        if 'network' in value:
            filedata = filedata.replace('[network]', '[network] \n' + key)
        if 'storage' in value:
            filedata = filedata.replace('[storage]', '[storage] \n' + key)
        if 'controller' in value:
            filedata = filedata.replace('[control]', '[control] \n' + key)
        if 'compute' in value:
#            filedata = filedata.replace('[compute]', '[compute] \n' + key)
            filedata = filedata.replace('[external-compute]', '[external-compute] \n' + key)
        if 'monitoring' in value:
            filedata = filedata.replace(
                '[monitoring]', '[monitoring] \n' + key)
    shutil.copy2(basefile, newfile)
    f = open(newfile, 'w')
    f.write(filedata)
    f.close()


def __validate_configuration(config):
    """
    This method is responsible for validating the information in input
    configuration file
    :param config : input configuration file
    :return : none or list of the ips
    """
    valid = True
    #variable to check storage node config in complete hosts list
    second_storage_config_present = False
    sriov_interface_present = False
    config_dict = config.get(consts.OPENSTACK)
    logger.debug("Starting validation")
    ip_list = []
    # Check if git_branch is defined
    if config_dict.get(consts.GIT_BRANCH) is None:
        logger.error("Value of git_branch not present")
        valid = False
    # Check if proxy values present
    proxy_dict = config_dict.get(consts.PROXIES)
    logger.info("======Your proxy settings for Cloud host machines are:======")
    logger.info(proxy_dict)

    # Check if  interfaces defined for each host
    hosts_list = config_dict.get(consts.HOSTS)
    logger.debug(hosts_list)
    for host in hosts_list:
        logger.debug("**********HOST INFORMATION************")
        logger.debug(host)
        host_dict = host.get(consts.HOST)
        logger.info(host_dict)
        #variable to check the storage node config per host
        is_storage_present       = False
        is_compute_present       = False
        is_storage_list_present  = False 
        logger.info(host_dict.items()) 
        for key, value in host_dict.items():
            if key == "interfaces":
                if len(value) < 2:
                    logger.error("Each host must have two interfaces")
                    valid = False
                # Iterating through interface information
                for interfaces in value:
                    logger.debug(interfaces.get(consts.TYPE))
                    if interfaces.get(consts.IP) is None and interfaces.get(
                            consts.TYPE) == "management":
                        logger.error(
                            "Ip must be defined for interface type:management")
                        valid = False
                    elif (interfaces.get(consts.TYPE).lower() != "management"
                          and interfaces.get(consts.TYPE).lower() != "data"
                          and interfaces.get(consts.TYPE).lower() != "tenant"):
                        logger.error("Invalid interface type")
                        valid = False
                    elif interfaces.get(consts.NAME) is None:
                        logger.error("Interface name must be defined")
                        valid = False
                    elif (interfaces.get(consts.IP) is not None
                          and interfaces.get(consts.TYPE) == "management"):
                        ip_list.append(interfaces.get('ip'))

            # Checking for other parameters in each host
            elif key == "hostname" and value is None:
                logger.error("Hostname must be defined")
                valid = False
            elif key == "password" and value is None:
                logger.error("password must be defined")
                valid = False
                logger.debug(value)
            elif key == "user":
                if value is None:
                    logger.error("User must be defined")
                    valid = False
            elif key == "node_type":
              logger.info(value)
              if(('storage' in value) or ('all' in value)):
                is_storage_present = True
              if(('compute' in value) or ('all' in value)):
                is_compute_present = True

            elif key=="second_storage":
              if ((value==None) and ("ceph" in config.get(consts.OPENSTACK ).get(consts.SERVICES)) and (is_storage_present==True)):
                  logger.info(value)
                  logger.info("SECOND STORAGE IS NOT DEFINED WHILE USING CEPH")
                  valid=False
              else:
                logger.info(value)
                is_storage_list_present = True
            #check if storage node configuration is present for this host, mark the variable as true
            elif key == "sriov_interface":
              if ((value==None) and ("sriov" in config.get(consts.OPENSTACK ).get(consts.SERVICES)) and (is_compute_present==True)):
                  valid = False
              else:
                logger.info(value)
                sriov_interface_present = True 
            if((is_storage_list_present == True) and (is_storage_present == True)):
              second_storage_config_present = True
        service = config.get(consts.OPENSTACK ).get(consts.SERVICES)
        if((config.get(consts.OPENSTACK ).get(consts.SERVICES) is not None) and  ("ceph" in config.get(consts.OPENSTACK ).get(consts.SERVICES)) and (is_storage_present==True)):
          if(((is_storage_present == False) and (is_storage_list_present == True)) or
             ((is_storage_present == True) and (is_storage_list_present == False))):
            logger.info("Error: When ceph is enabled Storage node_type(" '%s' ") and second_storage(" '%s' ") both should be present", is_storage_present, is_storage_list_present)
            valid=False
            exit(1)
    if((second_storage_config_present == False) and ("ceph" in config.get(consts.OPENSTACK ).get(consts.SERVICES))): 
       logger.info("Error: When ceph is enabled storage node_type and second_storage shall be present in one of the host")
       valid = False
       exit(1)
    
    if((sriov_interface_present == False) and ("sriov" in config.get(consts.OPENSTACK ).get(consts.SERVICES))):
       logger.error("When SRIOV is enabled, sriov_interface must be defined")
       valid = False
    
    if config_dict.get(consts.KOLLA).get(consts.BASE_DISTRIBUTION) is None:
        logger.info("KOLLA_BASE_DISTRO CANNOT BE NULL")
        valid = False
    if (config_dict.get(consts.KOLLA).get(
            consts.BASE_DISTRIBUTION) == 'ubuntu'
        or config_dict.get(consts.KOLLA).get(
                consts.BASE_DISTRIBUTION) == 'centos'):
        logger.info("VALID CONFIG")
    else:
        logger.info("NOT A VALID OPTION")
        valid = False
    if config_dict.get(consts.KOLLA).get(consts.INSTALL_TYPE) is None:
        logger.info("KOLLA_INSTALL_TYPE CANNOT BE NULL")
        valid = False
    if (config_dict.get(consts.KOLLA).get(consts.INSTALL_TYPE) == 'source'
            or config_dict.get(consts.KOLLA).get(
            consts.INSTALL_TYPE) == 'binary'):
        logger.info("VALID CONFIG")
    else:
        logger.info("NOT A VALID OPTION")
        valid = False
    if config_dict.get(consts.KOLLA).get(
            consts.KEEPALIVED_VIRTUAL_ROUTER_ID) is None:
        logger.info("VIRTUAL_ROUTER_ID CANNOT BE NULL")
        valid = False
    if config_dict.get(consts.KOLLA).get(
            consts.INTERNAL_VIP_ADDRESS) is None:
        logger.info("KOLLA_INTERNAL_VIP CANNOT BE NULL")
        valid = False
    if config_dict.get(consts.KOLLA).get(consts.REGISTRY) is None:
        logger.info("KOLLA_REGISTRY CANNOT BE NULL")
        valid = False
    if valid:
        return ip_list
    else:
        exit(1)


def __enable_key_ssh(config):
    command = "sed -i '/host_key_checking/c\#host_key_checking = False' "\
              + consts.ANSIBLE_CONF
    subprocess.call(command, shell=True)
    command_time = "sed -i '/#timeout = 10/c\\timeout = 50' "\
                   + consts.ANSIBLE_CONF
    subprocess.call(command_time, shell=True)
    hosts = config.get(consts.OPENSTACK).get(consts.HOSTS)
    for j in range(len(hosts)):
        user_name = hosts[j].get(consts.HOST).get(consts.USER)
        if user_name != 'root':
            logger.info('USER MUST BE ROOT')
            exit(0)
        password = hosts[j].get(consts.HOST).get(consts.PASSWORD)
        interfaces = hosts[j].get(consts.HOST).get(consts.INTERFACES)
        check_dir = os.path.isdir(consts.SSH_PATH)
        if not check_dir:
            os.makedirs(consts.SSH_PATH)
        for i in range(len(interfaces)):
            ip = interfaces[i].get(consts.IP)
            iface_type = interfaces[i].get(consts.TYPE)
            if iface_type == "management":
                host_ip = ip
                logger.info('GENERATING SSH KEY')
                subprocess.call(
                    'echo -e y|ssh-keygen -b 2048 -t rsa -f '
                    '/root/.ssh/id_rsa -q -N ""',
                    shell=True)
                logger.info('PUSHING KEY TO HOSTS')
                command = 'sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s' % (
                password, user_name, host_ip)
                res = subprocess.call(command, shell=True)
                if res != 0:
                    logger.info(
                        'ERROR IN PUSHING KEY:Probaly the key is already '
                        'present in remote host')
                logger.info('SSH KEY BASED AUTH ENABLED')
    return True


def clean_up(config, operation):
    """
    This method is used for cleanup of openstack services
    :param config: input configuration file
    :param operation:
    :return ret :t/f
    """

    if config:
        logger.info("Validating configuration")
    # validation
    list_ip, host_type = __hostip_list(config)
    docker_registry = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
        consts.REGISTRY)
    pull_from_hub = config.get(consts.OPENSTACK).get(consts.KOLLA).get(
        consts.PULL_HUB)
    host_node_type_map= __create_host_nodetype_map(config)
    host_storage_node_map = __create_host_storage_node_map(config, host_node_type_map)
    dpdk_enable=None
    service_list = config.get(consts.OPENSTACK).get(consts.SERVICES)
    if 'dpdk' in service_list:
      dpdk_enable="yes"
    if list_ip is None:
        logger.info("Not valid configurations")
        exit(1)
    else:
        logger.debug(
            "***********************CREDENTIALS**********************")
        logger.debug(list_ip)
        service_list = _getservice_list(config)
        logger.info(service_list)
        ret = ansible_configuration.clean_up_kolla(
            list_ip, docker_registry, service_list, operation,
            pull_from_hub, host_storage_node_map,dpdk_enable)
        return ret

def _getservice_list(config):
    service_str = ["Empty"]
    if config.get(consts.OPENSTACK).get(consts.SERVICES) is not None:
        service_str = config.get(consts.OPENSTACK).get(consts.SERVICES)
    return service_str

def upgrade_downgrade_cluster(config,version):
    hosts_list = config.get(consts.OPENSTACK).get(consts.HOSTS)
    controller_ip=""
    for host in hosts_list:
        host_data = host.get('host')
        node_type=host_data.get('node_type')
        for role in node_type:
            if  role == 'controller' :
               host_data = host.get('host')
               all_interface = host_data.get('interfaces')
               for interfaceData in all_interface:
                   if interfaceData.get('type') == 'management':
                        controller_ip=interfaceData.get('ip')
    if version == "upgrade":
       version="queens"
    else :
        version="pike"
    ret=ansible_configuration.launch_upgrade_downgrade_kolla(
            controller_ip, version)
    return ret

