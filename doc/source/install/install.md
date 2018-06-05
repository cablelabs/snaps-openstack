# Installation

## 1 Introduction

This document serves as a guide specifying the steps and configuration required
for OpenStack installation on servers configured by SNAPS-OpenStack. It does
not provide implementation level details.

This document is to be used by development team, validation and network test
teams.

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and
explained in below table.

| Convention | Usage |
| ---------- | ----- |
| Host Machines | Machines to be used for Openstack deployment. Openstack node controller, compute, storage and network node will be deployed on these machines. |
| Configuration node | Machine running installation scripts, Ansible, Python, NTP etc. |

### 1.2 Acronyms

The acronyms expanded below are fundamental to the information in this
document.

| Acronym | Explanation |
| ------- | ----------- |
| SNAPS | SDN/NFV Application Platform/Stack |
| IP | Internet Protocol |
| COTS | Commercial Off The Shelf |
| OS | OpenStack |
| VLAN | Virtual Local Area Network |

### 1.3 References

[1] OpenStack Installation guide:
https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html

### 1.4 OpenStack services support under QUEENS release
Basic OpenStack Services 
•	Nova
•	Neutron
•	Glance
•	Keystone
•	Horizon
•	Heat

Additional services:

•	Tacker
•	Mistral
•	Magnum
•	Barbican
•	Ceilometer
•    gnocchi
•    redis
•	Cinder
•	Ceph
�~@�    SRIOV


### 1.5 OpenStack IPv6 support under QUEENS release
 OpenStack Queens release supports IPV6 functionality for OpenStack(Current support is availbale only for VM to VM networking)


## 2 Environment Prerequisites

### 2.1 Hardware Requirements

The current release of SNAPS-OpenStack is tested on the following platform.

**Compute Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 16GB RAM, 80+ GB Hard disk with 3 network cards. Server should be network boot Enabled and IPMI capable. |

**Controller Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 16GB RAM, 80+ GB Hard disk with 3 network cards. Server should be network boot Enabled and IPMI capable |

**Configuration Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 16GB RAM, 80+ GB Hard disk with 1 network cards. |

### 2.2 Software Requirements

| Category | Software version |
| -------- | ---------------- |
| Operating System | Ubuntu 16.04 |
| Scripting |  Python 2.7 |
| Framework | Ansible 2.3.0.0 |
| OpenStack | Queens |

## 2.3 Pre-requsites Requirements

- Machine running SNAPS-OpenStack should have Ubuntu 16.04 Xenial as host OS
  and should have internet access.
- All host machines should have identical interface names and should have at
  least 2 interfaces (one for management and one for data).
- All host machines are connected to configuration node (machine running
  SNAPS-OpenStack) and have Internet access connectivity via data interface.

> Note: Configuration node should have http/https and ftp proxy if node is
> behind corporate firewall. Set the http/https proxy for apt.


## 3 Configuration

### 3.1 deployment.yaml

Configuration file used by SNAPS-OpenStack for OpenStack provisioning. Options
defined here are used by SNAPS-OpenStack to deploy appropriate OpenStack
services on host machines and configuring them to be controller, compute or
storage nodes.

#### OpenStack:

Parameters defined in this section allow user to specify deployment type for
OpenStack services and OpenStack version. Configuration parameters defined in
this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| deployement_type | N | OpenStack deployment type, `Devstack` or `Kolla`. |
| git_branch | N | OpenStack release to clone (In current release only Queens is supported so it will be `stable/queens`). |
| kolla_tag | Y | kolla package release to clone through kolla_tag value. |
| kolla_ansible_tag | Y | kolla-ansible package release to clone through kolla_ansible_tag value. |

#### hosts:

This section is used for OpenStack environment planning. Parameters defined
here configure host machines as OpenStack controller, compute, storage and
network node. Configuration parameters defined in this section are explained
below.

<table>
  <tr>
    <th colspan="3">Parameter</th>
    <th>Optionality</th>
    <th>Description</th>
  </tr>
  <tr>
    <td colspan="4">host</td>
    <td>Define this set of parameters for each host machine (a separate host section should be defined for each host machine).</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">hostname</td>
    <td>N</td>
    <td>Hostname to be used for the machine. SNAPS-OpenStack assigns this hostname to the machine.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="3">interfaces</td>
    <td>Define this set of parameters for each interface of the host machine.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>ip</td>
    <td>N</td>
    <td>IP of the primary interface (Management Interface, allocated after OS provisioning).</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>name</td>
    <td>N</td>
    <td>Name of the primary interface.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>type</td>
    <td>N</td>
    <td>Traffic type (<code>management</code>).</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>gateway</td>
    <td>N</td>
    <td>Gateway Ip of the subnet.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>ip</td>
    <td>N</td>
    <td>IP of the 2nd interface (External Network).</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>name</td>
    <td>N</td>
    <td>Name of 2nd interface.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>type</td>
    <td>N</td>
    <td>Traffic type (<code>data</code>).</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>ip</td>
    <td>Y</td>
    <td>IP of 3rd interface (Tenant Network).</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>name</td>
    <td>Y</td>
    <td>Name of the interface.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>type</td>
    <td>Y</td>
    <td>Traffic type (<code>tennant</code>).</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">node_type</td>
    <td>N</td>
    <td>List of nodes to be setup on this host machine. User can choose any combination of <code>controller</code>, <code>compute</code>, <code>network</code> and <code>storage</code> values. If user wishes to deploy a single node setup, he should use value <code>all</code>.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">second_storage</td>
    <td>Y</td>
    <td>List of Mount point of secondary storage for ceph. Has to be present if the node_type is "storage"</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">sriov_interface</td>
    <td>Y</td>
    <td>List of SRIOV interface for SRIOV. Has to be present if the SRIOV is enabled</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">service_host</td>
    <td>Y</td>
    <td>IP of controller machine. Not required if the machine is controller.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">user</td>
    <td>N</td>
    <td>User of host machine.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">password</td>
    <td>N</td>
    <td>Password for host machine user.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">isolcpus</td>
    <td>Y</td>
    <td>CPUs to be pinned for VMs on this host machine.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">reserved_host_memory_mb</td>
    <td>Y</td>
    <td>RAM to be reserved for VMs on this host machine.</td>
  </tr>
</table>

#### networks

SNAPS-OpenStack uses this section to define external and tenant networks for
OpenStack VMs. This section is optional, if user does not provide this section,
SNAPS-OpenStack will create default network. Configuration parameters defined in
this section are explained below.

#### external

<table>
  <tr>
    <th colspan="2">Parameter</th>
    <th>Optionality</th>
    <th>Description</th>
  </tr>
  <tr>
    <td colspan="2">gateway</td>
    <td>N</td>
    <td>Gateway IP for external network.</td>
  </tr>
  <tr>
    <td colspan="2">ip_pool</td>
    <td/>
    <td/>
  </tr>
  <tr>
    <td/>
    <td>End</td>
    <td>N</td>
    <td>Last address for DHCP range.</td>
  </tr>
  <tr>
    <td/>
    <td>Start</td>
    <td>N</td>
    <td>First address for DHCP range.</td>
  </tr>
  <tr>
    <td colspan="2">Subnet</td>
    <td>N</td>
    <td>Subnet in CIDR notation.</td>
  </tr>
</table>

#### tenant

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| Subnet | N | Subnet in CIDR notation. |
| subnet_size | N | Size of subnet. |

#### mtu_size

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| default | N | Default MTU size to be used on provider networks.|
| vxlan | N | MTU size to be used on overlay networks.|

> Note: Default mtu size value should be at least 50 greater than vxlan mtu size.

#### proxies

This section defines environment proxies to be exported on all host machines.
Configuration parameters defined in this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| ftp_proxy | Y | Proxy to be used for FTP. |
| http_proxy | Y | Proxy to be used for HTTP traffic. |
| https_proxy | Y | Proxy to be used for HTTPS traffic. |
| no_proxy | N | Comma separated list of IPs of all host machines. Localhost `127.0.0.1` should be included here. |

> Note: use proxy only when direct access to internet not available.

#### service_password

Password to be used for OpenStack service endpoints.

#### services

Defines the additional services to be installed. Allowed values are `magnum`,
`telemetry`, `cinder` etc. See sample below:

```
services:
  - magnum
  - tempest
  - ceilometer
  - cinder
  - tacker
  - ceph
  - sriov
```

#### kolla

This section is required only for Kolla based OpenStack deployment.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| base_distro | N | Should be `ubuntu`. |
| install_type | N | Should be `source`. |
| keepalived_virtual_router_id | N | Should be kept as `10`. |
| internal_vip_address | N | Any unused IP address in the management network. |
| kolla_registry | N | IP of node where docker registry has to be created. In current version it should be controller node IP. |
| kolla_registry_port | N | Port to be used for docker registry. |
| internal_interface | N | Interface for the OpenStack internal api end points. |
| external_vip_address | N | Ip address for OpenStack external end points. |
| external_interface | N | Interface for the OpenStack external api end points. |
| base_size | Y | Base size for the physical volume of the cinder. |
| pull_from_hub | Y | Pull images from docker hub for deployment if set to yes (Values can be yes/no). |
| count | Y | Total count for the physical volume created. |

### 3.2 var.yaml (VLAN Configuration)

Configuration file used by SNAPS-OpenStack for VLAN based tenant network
provisioning.

#### TASKS

Parameters defined in this section allow user to specify post deployment tasks
(VLAN configuration). Configuration parameters defined in this section are
explained below:

<table>
  <tr>
    <th colspan="3">Parameter</th>
    <th>Optionality</th>
    <th>Description</th>
  </tr>
  <tr>
    <td colspan="3">name</td>
    <td>N</td>
    <td>Should be <code>TenantVLAN</code>.</td>
  </tr>
  <tr>
    <td colspan="3">physical_network</td>
    <td>N</td>
    <td>Should be <code>name of physical network to be used for VLAN</code>.</td>
  </tr>
  <tr>
    <td colspan="3">min_vlan_id</td>
    <td>N</td>
    <td>Should be <code>minimum value of vlan id to be used</code>.</td>
  </tr>
  <tr>
    <td colspan="3">max_vlan_id</td>
    <td>N</td>
    <td>Should be <code>maximum value of vlan id to be used</code>.</td>
  </tr>
  <tr>
    <td colspan="4">host</td>
    <td>Define this set of parameters for each host machine (A separate host section should be defined for each host machine).</td>
  </tr>
  <tr>
    <td/>
    <td colspan="3">interfaces</td>
    <td>Define this set of parameters for each VLAN.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>port_name</td>
    <td>N</td>
    <td>Interface name attached to the vlan.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>size</td>
    <td>N</td>
    <td>Vlan MTU size.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">ip</td>
    <td>Y</td>
    <td>IP of Management network.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">username</td>
    <td>N</td>
    <td>User of host machine.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">password</td>
    <td>N</td>
    <td>Password for host machine user.</td>
  </tr>
</table>

### 3.3 var.yaml (MTU settings)

Configuration file used by SNAPS-OpenStack for MTU size configuration of
physical NICs.

#### TASKS

Parameters defined in this section allows user to specify post deployment tasks
(MTU settings). Configuration parameters defined in this section are explained
below.

<table>
  <tr>
    <th colspan="3">Parameter</th>
    <th>Optionality</th>
    <th>Description</th>
  </tr>
  <tr>
    <td colspan="3">name</td>
    <td>N</td>
    <td>Should be <code>mtu</code>.</td>
  </tr>
  <tr>
    <td colspan="4">host</td>
    <td>Define this set of parameters for each host machine (A separate host section should be defined for each host machine).</td>
  </tr>
  <tr>
    <td/>
    <td colspan="3">interfaces</td>
    <td>Define this set of parameters for each interface to be reconfigured for MTU size.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>port_name</td>
    <td>N</td>
    <td>Interface name attached to the vlan.</td>
  </tr>
  <tr>
    <td/>
    <td/>
    <td>size</td>
    <td>N</td>
    <td>MTU size.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">ip</td>
    <td>Y</td>
    <td>IP of Management network.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">username</td>
    <td>N</td>
    <td>User of host machine.</td>
  </tr>
  <tr>
    <td/>
    <td colspan="2">password</td>
    <td>N</td>
    <td>Password for host machine user.</td>
  </tr>
</table>

## 4 Installation Steps

### 4.1 Fresh OpenStack Installation

#### Step 1

Clone/FTP Openstack_Provisioning package on configuration node. All operations
of configuration server expect the user should be explicitly switched (using
`su root`) to the root user.

#### Step 2

Go to directory `<repo_dir>/conf/openstack/kolla`

Modify file `deployment.yaml` for provisioning of OpenStack nodes on cloud
cluster host machines (controller node, compute nodes). Modify this file
according to your set up environment only (Refer section 3).

#### Step 3

Run `iaas_launch.py` as shown below:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -drs
```

This will install Kolla OpenStack service on host machines. Your OpenStack
installation will start and will get completed in ~40 minutes.

### 4.2 VLAN Tenant Network Configuration

#### Step 1

Go to `<repo_dir>/snaps_openstack/utilities/` directory.

Define VLAN ports per host in `var.yaml` file under TenantVLAN task (we can
define multiple vlan ports for multiple hosts).

#### Step 2

Run `network_config.py` as shown below:

```
sudo python <repo_dir>/network_config.py -f <repo_dir>/snaps_openstack/utilities/var.yaml -tvlan
```

Please configure the switch for tagged vlan ports.

### 4.3 MTU Size Settings for Physical NICs

#### Step 1

Go to `<repo_dir>/snaps_openstack/utilities/` directory.

Define MTU size for NICS per host in `var.yaml` file under mtu task.

#### Step 2

Run `network_config.py` as shown below:

```
sudo python <repo_dir>/network_config.py -f <repo_dir>/snaps_openstack/utilities/var.yaml -mtu
```

## 5 Cleanup and Troubleshooting

### 5.1 Fresh Deployment with Existing Docker Repository

If docker based images for OpenStack services are already available run
`iaas_launch.py` as shown below:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -d
```

### 5.2 Re-deployment

In case previous deployment attempt has failed or new changes are required
(enabling optional services), attempt following steps.

First, Clean up previous OpenStack deployment:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -c
```

Or Clean up previous deployment along with docker repository:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -drc
```

Then, re-install OpenStack. If docker repository exists:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -d
```

Or if docker repository needs to be built:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -drs
```

### 5.3 Cleanup

Clean up previous OpenStack deployment:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -c
```

Clean up previous deployment along with docker repository:

```
sudo python <repo_dir>/iaas_launch.py -f <repo_dir>/conf/openstack/kolla/deployment.yaml -drc
```

Clean up previous vlan configuration:

```
sudo python <repo_dir>/network_config.py -f <repo_dir>/snaps_openstack/utilities/var.yaml -tvclean
```

#### 5.3.1 Vlan Mapping Cleanup

Only perform the steps below after you've run vlan configuration cleanup script as instructed
in 5.3 above. The manual cleanup steps in this section are necessary to workaround an upstream
defect in https://bugs.launchpad.net/neutron/+bug/1743425:

Ssh to control node:
```
sudo ssh <control-node-ip>
```

Obtain the maria db root credential:
```
grep wsrep_sst_auth /etc/kolla/mariadb/galera.cnf | cut -d":" -f2
```

Run interactive bash shell from mariadb container:
```
docker exec -ti mariadb bash
```

Connect to neutron DB as root (enter maria db root credential when prompted):
```
mysql neutron -u root -p
```

Remove vlan mappings from neutron DB:
```
TRUNCATE TABLE ml2_vlan_allocations;
```

Exit from neutron DB:
```
exit
```

Exit from mariadb container interactive mode:
```
exit
```
