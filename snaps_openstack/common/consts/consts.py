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
Project constants
"""
from pathlib import Path

p = str(Path(__file__).parents[2])
CWD = p + "/"
OPENSTACK = "openstack"
PROXIES = "proxies"
HTTP_PROXY = "http_proxy"
HTTPS_PROXY = "https_proxy"
FTP_PROXY = "ftp_proxy"
NO_PROXY = "no_proxy"
HOSTS = "hosts"
HOST = "host"
INTERFACES = "interfaces"
SRIOV_INTERFACE = "sriov_interface"
NOVA_STRING = "nova_str"
SRIOV_STRING = "sriov_str"
NODE_TYPE = "node_type"
IP = "ip"
TYPE = "type"
GIT_BRANCH = "git_branch"
KOLLA_TAG = "kolla_tag"
KOLLA_ANSIBLE_TAG = "kolla_ansible_tag"
HOSTNAME = "hostname"
NAME = "name"
USER = "user"
PASSWORD = "password"
ANSIBLE_CONF = "/etc/ansible/ansible.cfg"

ANSIBLE_PKG = 'snaps_openstack.ansible_p'
ANSIBLE_UTILS_PKG = ANSIBLE_PKG + '.ansible_utils'
PROXY_DATA_FILE = 'proxy_data.yaml'
VARIABLE_FILE = 'variable.yaml'
BASE_SIZE = "base_size"
COUNT = "count"
KOLLA = "kolla"
SERVICES = "services"

BASE_DISTRIBUTION = "base_distro"
INSTALL_TYPE = "install_type"
KEEPALIVED_VIRTUAL_ROUTER_ID = "keepalived_virtual_router_id"
INTERNAL_VIP_ADDRESS = "internal_vip_address"
EXTERNAL_VIP_ADDRESS = "external_vip_address"
EXTERNAL_INTERFACE = "external_interface"
REGISTRY = "kolla_registry"

KOLLA_SOURCE_PATH = CWD + "packages/source/"

DAEMON_FILE = KOLLA_SOURCE_PATH + "daemon.json"
GLOBAL_BASE_FILE = KOLLA_SOURCE_PATH + "globals_bak.yml"
GLOBAL_FILE = KOLLA_SOURCE_PATH + "globals.yml"
NETVAR_FILE = KOLLA_SOURCE_PATH + "netvars.yml"
INVENTORY_SOURCE_FOLDER = KOLLA_SOURCE_PATH + "inventory/"
INVENTORY_MULTINODE_BASE_FILE = INVENTORY_SOURCE_FOLDER + "multinode_bak"
INVENTORY_MULTINODE_FILE = INVENTORY_SOURCE_FOLDER + "multinode"

KOLLA_PB_PKG = ANSIBLE_PKG + '.commission.openstack.playbooks.deploy_mode.kolla'
MULTI_NODE_KOLLA_ISO_NWK_YAML = "multinode_kolla_iso_network.yaml"
MULTI_NODE_KOLLA_COMPUTE_YAML = "multinode_kolla_compute.yaml"
MULTI_NODE_KOLLA_CONTROLLER_YAML = "multinode_kolla_controller.yaml"
SINGLE_NODE_KOLLA_YAML = "single_node_kolla.yaml"
KOLLA_SET_HOSTS = "kolla_sethosts.yaml"
KOLLA_SET_HOSTSNAME = "kolla_sethostsname.yaml"
KOLLA_SET_REGISTRY = "setup_registry.yaml"
KOLLA_SET_KOLLA = "setup_kolla.yaml"
KOLLA_SET_STORAGE = "setup_storage.yaml"
KOLLA_CLEANUP_HOSTS = "cleanup_hosts.yaml"
KOLLA_REMOVE_REGISTRY = "remove_registry.yaml"
KOLLA_REMOVE_STORAGE = "cleanup_storage.yaml"
KOLLA_COPY_KEY = "copy_key_gen.yaml"
KOLLA_PUSH_KEY = "push_key_gen.yaml"
KOLLA_REMOVE_IMAGES = "remove_images.yaml"
KOLLA_SET_PIN = "kolla_set_pin.yaml"
KOLLA_CEPH_SETUP = "ceph_setup.yaml"
SSH_PATH = "/root/.ssh"
KOLLA_REGISTRY_PORT = "kolla_registry_port"
PULL_HUB = "pull_from_hub"
SECOND_STORAGE="second_storage"
OPENSTACK_INSTALLATION_LOGS = CWD + "installation_logs.log"
