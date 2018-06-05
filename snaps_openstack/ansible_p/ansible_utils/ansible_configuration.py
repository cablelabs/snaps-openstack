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

# This script is responsible for preparing all the files and variables neede
# for devstack deployment and calling the user defined  methods for the
# devstack deployment

import logging

import pkg_resources

import ansible_playbook_launcher as apbl
from snaps_openstack.common.consts import consts

logger = logging.getLogger('deploy_ansible_configuration')

variable_file = pkg_resources.resource_filename(
    consts.ANSIBLE_UTILS_PKG, consts.VARIABLE_FILE)
proxy_data_file = pkg_resources.resource_filename(
    consts.ANSIBLE_UTILS_PKG, consts.PROXY_DATA_FILE)


def provision_preparation(proxy_dict, user_dict):
    """
    This method is responsible for writing the hosts info in ansible hosts file
    proxy inf in ansible proxy file
    set the git branch version in devstack_preparation_file
    : param proxy_dict: proxy data in the dictionary format
    : user_dict: user credential in dictionary format
    : return ret :
    """

    # code which adds ip to the /etc/anisble/hosts file
    ret = False

    if proxy_dict:
        logger.debug("Adding proxies")
        proxy_file_in = open(proxy_data_file, "r+")
        proxy_file_in.seek(0)
        proxy_file_in.truncate()
        proxy_file_out = open(proxy_data_file, "w")
        proxy_file_out.write("---")
        proxy_file_out.write("\n")
        for key, value in proxy_dict.items():
            logger.debug("Proxies added in file:" + key + ":" + value)
            proxy_file_out.write(key + ": " + str(value) + "\n")
        proxy_file_out.close()
        proxy_file_in.close()
    if not user_dict:
        return ret


def clean_up_kolla(list_ip, git_branch, docker_registry, service_list,
                   operation, pull_from_hub, host_storage_node_map,dpdk_enable):
    """
    This method is responsible for the cleanup of openstack services
    """
    if list_ip:
        cleanup_hosts_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_CLEANUP_HOSTS)
        ret = apbl.launch_ansible_playbook(
            list_ip, cleanup_hosts_pb, {
                'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file,
                'GIT_BRANCH': git_branch,'DPDK_ENABLE':dpdk_enable})
        if ret != 0:
            logger.info('FAILED IN CLEANUP')
            exit(1)
        if 'cinder' in service_list:
            for key,value in host_storage_node_map.iteritems():
               ip = key
               second_storage = value
               logger.info(ip)
               logger.info(second_storage)   
               remove_storage_pb = pkg_resources.resource_filename(
                   consts.KOLLA_PB_PKG, consts.KOLLA_REMOVE_STORAGE)
               ret_storage = apbl.launch_ansible_playbook(
                   list_ip, remove_storage_pb, {
                       'target': ip,
                       'PROXY_DATA_FILE': proxy_data_file,
                       'VARIABLE_FILE': variable_file,
                       'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                       'SECOND_STORAGE': second_storage})
               if ret_storage != 0:
                   logger.info('FAILED')
                   exit(1)

        remove_images_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_REMOVE_IMAGES)

        if operation is "cleanregistry" and pull_from_hub != "yes":
            remove_registry_pb = pkg_resources.resource_filename(
                consts.KOLLA_PB_PKG, consts.KOLLA_REMOVE_REGISTRY)

            ret1 = apbl.launch_ansible_playbook(
                list_ip, remove_registry_pb, {
                    'target': docker_registry,
                    'PROXY_DATA_FILE': proxy_data_file,
                    'VARIABLE_FILE': variable_file})
            if ret1 != 0:
                logger.info('Regsitery cleanup problems might be there')

            ret_image = apbl.launch_ansible_playbook(
                list_ip, remove_images_pb,
                {'PROXY_DATA_FILE': proxy_data_file,
                 'VARIABLE_FILE': variable_file})
            if ret_image != 0:
                logger.info('Image cleanup problems might be there')
        elif operation is "cleanregistry" and pull_from_hub == "yes":
            ret_image = apbl.launch_ansible_playbook(
                list_ip, remove_images_pb, {
                    'PROXY_DATA_FILE': proxy_data_file,
                    'VARIABLE_FILE': variable_file})
            if ret_image != 0:
                logger.info('Image cleanup problems might be there')


# TODO - Try breaking this function into smaller ones
def launch_provisioning_kolla(iplist, git_branch, kolla_tag, kolla_ansible_tag,
                              host_name_map, host_node_type_map,
                              docker_registry, docker_port, kolla_base,
                              kolla_install, ext_sub, ext_gw, ip_pool_start,
                              ip_pool_end, operation,
                              host_cpu_map, reserve_memory, base_size, count,
                              default, vxlan, pull_from_hub, host_storage_node_map, host_sriov_interface_node_map,
							  dpdk_enable):
    if pull_from_hub != "yes":
        docker_opts = "--insecure-registry  " + docker_registry + ":" + str(
            docker_port)
        docker_registry_ip = docker_registry + ":" + str(docker_port)
    else:
        docker_opts = ""
        docker_registry_ip = ""

    list_network = []
    list_storage = []
    list_node = []
    list_all = []
    list_controller = []
    list_compute = []
    ip_control = None
    second_storage = None 
    for key, value in host_name_map.items():
        ip = value
        host_name = key
        logger.info('EXECUTING SET HOSTS PLAY')
        logger.info(consts.KOLLA_SET_HOSTS)

        set_hosts_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_SET_HOSTS)
        ret_hosts = apbl.launch_ansible_playbook(
            iplist, set_hosts_pb, {
                'target': ip, 'host_name': host_name,
                'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file,
                'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH})
        if ret_hosts != 0:
            logger.info("FAILED IN SETTING HOSTS FILE")
            exit(1)
        else:
            logger.info('SET HOSTNAME IN HOSTS')

        set_hostname_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_SET_HOSTSNAME)
        apbl.launch_ansible_playbook(
            iplist, set_hostname_pb, {
                'target': ip, 'host_name': host_name,
                'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file})
    for key, value in host_node_type_map.items():
        ip = key
        node_type = value
        if len(host_node_type_map) == 1:
            list_all.append(ip)
            ip_control = ip
        if 'compute' in node_type:
            list_compute.append(ip)
        if 'controller' in node_type:
            list_controller.append(ip)
            ip_control = ip
        if 'network' in node_type:
            list_network.append(ip)
        if 'storage' in node_type:
            list_storage.append(ip)
        if 'controller' not in node_type:
            list_node.append(ip)
    logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++')
    logger.info(list_all)
    logger.info(list_compute)
    logger.info(list_controller)
    logger.info(list_node)
    logger.info(list_storage)
    if ip_control in list_compute:
        check_var = 'present'
        logger.info('controller also a compute')
        logger.info(ip_control)
    else:
        check_var = 'absent'
        logger.info('controller not a compute')
    if ip_control != docker_registry:
        get_tag = False
        logger.info("IMAGE SERVER IS DIFFERENT THAN CONTROLLER")
        logger.info(get_tag)
    else:
        get_tag = True
        logger.info(get_tag)
    logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++')
    logger.info('SETUP KOLLA BASE PACKAGES')
    if pull_from_hub != "yes":
        set_kolla_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_SET_KOLLA)
        ret = apbl.launch_ansible_playbook(
            iplist, set_kolla_pb, {
                'target': docker_registry, 'DOCKER_OPTS': docker_opts,
                'DOCKER_REGISTRY_IP': docker_registry_ip,
                'kolla_base': kolla_base, 'kolla_install': kolla_install,
                'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file,
                'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                'GIT_BRANCH': git_branch,
                'KOLLA_TAG': kolla_tag,
                'KOLLA_ANSIBLE_TAG': kolla_ansible_tag,
                'LIST_ALL':iplist})
        logger.info(ret)
        print('#####################################################')
        if ret != 0:
            logger.info('FAILED IN SETTING KOLLA BASE PACKAGES')
            exit(1)

    if operation is "deployregistry" and pull_from_hub != "yes":
        logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++')
        logger.info(
            'SETUP REGISTRY:It will take bit time to setup your registry with '
            'comipled images')

        set_registry_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_SET_REGISTRY)
        ret = apbl.launch_ansible_playbook(
            iplist, set_registry_pb, {
                'target': docker_registry, 'DOCKER_OPTS': docker_opts,
                'DOCKER_REGISTRY_IP': docker_registry_ip,
                'kolla_base': kolla_base, 'kolla_install': kolla_install,
                'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file,
                'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                'PULL_HUB': pull_from_hub})
        logger.info(ret)
        print('#####################################################')
        if ret != 0:
            logger.info('FAILED IN SETTING DOCKER REGISTRY')
            exit(1)

    copy_key_pb = pkg_resources.resource_filename(
        consts.KOLLA_PB_PKG, consts.KOLLA_COPY_KEY)
    apbl.launch_ansible_playbook(
        iplist, copy_key_pb, {
            'target': ip_control, 'PROXY_DATA_FILE': proxy_data_file,
            'VARIABLE_FILE': variable_file})
    for key_ip in iplist:
        push_key_pb = pkg_resources.resource_filename(
            consts.KOLLA_PB_PKG, consts.KOLLA_PUSH_KEY)
        apbl.launch_ansible_playbook(
            iplist, push_key_pb, {
                'target': key_ip, 'PROXY_DATA_FILE': proxy_data_file,
                'VARIABLE_FILE': variable_file})

    if not list_all:
        logger.info(
            '**********************MULTINODE_DEPLOYMENT**********************')
        if list_storage:
            for storage_ip in list_storage:
              for key,value in host_storage_node_map.iteritems():
                if key is storage_ip:
                  second_storage=value 
                  set_storage_pb = pkg_resources.resource_filename(
                    consts.KOLLA_PB_PKG, consts.KOLLA_SET_STORAGE)
                  ret_storage = apbl.launch_ansible_playbook(
                    iplist, set_storage_pb, {
                        'target': storage_ip,
                        'PROXY_DATA_FILE': proxy_data_file,
                        'VARIABLE_FILE': variable_file,
                        'SECOND_STORAGE': second_storage,
                        'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                        'OPERATION': operation, 'BASE_SIZE': base_size,
                        'COUNT': count})

                  if ret_storage != 0:
                    logger.info("FAILED IN SETTING STORAGE")
                    exit(1)
        if git_branch.lower() == 'stable/queens':
        
            for node_ip in list_node:
              for key,value in host_sriov_interface_node_map.iteritems():
                if key is node_ip:
                   sriov_interface=value
                   multi_node_pb = pkg_resources.resource_filename(
                       consts.KOLLA_PB_PKG,
                       consts.MULTI_NODE_KOLLA_COMPUTE_YAML)
                   ret = apbl.launch_ansible_playbook(
                     iplist, multi_node_pb, {
                         'DOCKER_OPTS': docker_opts,
                         'DOCKER_REGISTRY_IP': docker_registry_ip,
                         'target': node_ip,
                         'PROXY_DATA_FILE': proxy_data_file,
                         'VARIABLE_FILE': variable_file,
                         'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                         'SECOND_STORAGE': second_storage,
                         'BASE_SIZE': base_size,
                         'COUNT': count, 'GIT_BRANCH': git_branch,
                         'KOLLA_TAG': kolla_tag,
                         'KOLLA_ANSIBLE_TAG': kolla_ansible_tag,
                         'DEFAULT': default, 'VXLAN': vxlan,
                         'PULL_HUB': pull_from_hub,
                         'SRIOV_INTERFACE': sriov_interface})

                if ret != 0:
                    print(ret)
                    logger.info("FAILED IN COMPUTE QUEENS")
                    exit(1)
                else:
                    logger.info(
                        "***********PLAYBOOK EXECUTED SUCCESSFULLY***********")
        for controller_ip in list_controller:
            if len(list_storage) == 1:
                ceph_pb = pkg_resources.resource_filename(
                    consts.KOLLA_PB_PKG, consts.KOLLA_CEPH_SETUP)
                apbl.launch_ansible_playbook(
                    iplist, ceph_pb, {
                        'target': controller_ip,
                        'VARIABLE_FILE': variable_file,
                        'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH})
            if git_branch.lower() == 'stable/queens':
                for key,value in host_sriov_interface_node_map.iteritems():
                  if key is node_ip:
                     sriov_interface=value
                     nova_str = ""
                     sriov_str = ""
                    
                     if sriov_interface is not None: 
                       for iface in sriov_interface:
                         nova_str = nova_str +  "{\"devname\":\"" + iface +"\", \"physical_network\": \"physnet1\"},"
                         sriov_str = sriov_str+"physnet1:"+iface+","

                       sriov_str = sriov_str.rstrip(",")
                       nova_str = "[" + nova_str.rstrip(",") + "]"

                multi_node_pb = pkg_resources.resource_filename(
                    consts.KOLLA_PB_PKG,
                    consts.MULTI_NODE_KOLLA_CONTROLLER_YAML)
                ret_controller = apbl.launch_ansible_playbook(
                    iplist, multi_node_pb,
                    {'target': controller_ip, 'DOCKER_OPTS': docker_opts,
                     'DOCKER_REGISTRY_IP': docker_registry_ip,
                     'kolla_base': kolla_base, 'kolla_install': kolla_install,
                     'PROXY_DATA_FILE': proxy_data_file,
                     'VARIABLE_FILE': variable_file,
                     'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                     'EXT_SUB': ext_sub, 'EXT_GW': ext_gw,
                     'START_IP': ip_pool_start, 'END_IP': ip_pool_end,
                     'DEFAULT': default, 'VXLAN': vxlan,
                     'GIT_BRANCH': git_branch, 'KOLLA_TAG': kolla_tag,
                     'KOLLA_ANSIBLE_TAG': kolla_ansible_tag,
                     'CHECK_VAR': check_var, 'PULL_HUB': pull_from_hub,
                     'GET_TAG': get_tag, 'SRIOV_INTERFACE': sriov_interface,
                     'SRIOV_STRING': sriov_str,'NOVA_STRING': nova_str})
                if ret_controller != 0:
                    logger.info("FAILED IN CONTROLLER QUEENS")
                    print(ret_controller)
                    exit(1)
        for node_ip in list_node:
           if dpdk_enable!="yes":
              multi_node_pb = pkg_resources.resource_filename(
                  consts.KOLLA_PB_PKG,
                  consts.MULTI_NODE_KOLLA_ISO_NWK_YAML)
              ret = apbl.launch_ansible_playbook(
                  iplist, multi_node_pb, {
                      'target': node_ip,
                      'PROXY_DATA_FILE': proxy_data_file,
                      'VARIABLE_FILE': variable_file,
                      'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH})
              if ret != 0:
                  logger.error("NETWORK ADAPTATION FAILED IN COMPUTE")
                  exit(1)
              else:
                  logger.info(
                      "*********ISO NWK PLAYBOOK EXECUTED SUCCESSFULLY*********")

        for node_ip in list_compute:
            for key,value in host_sriov_interface_node_map.iteritems():
                if key is node_ip:
                   sriov_interface=value
                   nova_str = ""
                   sriov_str = ""
                   if sriov_interface is not None: 
                       for iface in sriov_interface:
                         nova_str = nova_str +  "{\"devname\":\"" + iface +"\", \"physical_network\": \"physnet1\"},"
                         sriov_str = sriov_str+"physnet1:"+iface+","

                       sriov_str = sriov_str.rstrip(",")
                       nova_str = "[" + nova_str.rstrip(",") + "]"

            vcpu_pin = host_cpu_map.get(node_ip)
            memory = reserve_memory.get(node_ip)
            set_pin_pb = pkg_resources.resource_filename(
                consts.KOLLA_PB_PKG, consts.KOLLA_SET_PIN)
            ret = apbl.launch_ansible_playbook(
                iplist, set_pin_pb, {
                    'target': node_ip,
                    'PROXY_DATA_FILE': proxy_data_file,
                    'VARIABLE_FILE': variable_file,
                    'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                    'vcpu_pin': vcpu_pin, 'memory': memory,
                    'DEFAULT': default, 'VXLAN': vxlan,
                    'GIT_BRANCH': git_branch, 'KOLLA_TAG': kolla_tag,
                    'KOLLA_ANSIBLE_TAG': kolla_ansible_tag,
                    'SRIOV_STRING': sriov_str,'NOVA_STRING': nova_str,
                    'CONTROLLER_IP': ip_control})
            if ret != 0:
                logger.error(" FAILED IN COMPUTE")
                exit(1)
            else:
                logger.info(
                    "*****************EXECUTED SUCCESSFULLY*****************")
    else:
        logger.info('ALL IN ONE DEPLOYEMENT')
        if(len(host_storage_node_map)==1):
          second_storage=host_storage_node_map.values()[0]
          logger.info(host_storage_node_map)
          logger.info(second_storage)
        else:
          logger.info("Failed in creating storage map")
          exit(1)

        if git_branch.lower() == 'stable/queens':
            single_node_pb = pkg_resources.resource_filename(
                consts.KOLLA_PB_PKG, consts.SINGLE_NODE_KOLLA_YAML)
            ret_all = apbl.launch_ansible_playbook(
                list_all, single_node_pb, {
                    'DOCKER_OPTS': docker_opts,
                    'DOCKER_REGISTRY_IP': docker_registry_ip,
                    'kolla_base': kolla_base, 'kolla_install': kolla_install,
                    'PROXY_DATA_FILE': proxy_data_file,
                    'VARIABLE_FILE': variable_file,
                    'BASE_FILE_PATH': consts.KOLLA_SOURCE_PATH,
                    'EXT_SUB': ext_sub, 'EXT_GW': ext_gw,
                    'START_IP': ip_pool_start, 'END_IP': ip_pool_end,
                    'SECOND_STORAGE': second_storage, 'BASE_SIZE': base_size,
                    'COUNT': count, 'DEFAULT': default,
                    'VXLAN': vxlan, 'GIT_BRANCH': git_branch,
                    'KOLLA_TAG': kolla_tag,
                    'KOLLA_ANSIBLE_TAG': kolla_ansible_tag,
                    'PULL_HUB': pull_from_hub})
            if ret_all != 0:
                logger.info("FAILED IN DEPLOYMENT QUEENS")
                print(ret_all)
                exit(1)
            else:
                logger.info("SINGLE NODE COMPLETED QUEENS")

    logger.info("PROCESS COMPLETE")
