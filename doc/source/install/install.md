# Installation

## 1 Introduction

This document serve as a guide specifying the steps and configuration required for OpenStack installation on servers configured by SNAPS-Kolla. It does not provide implementation level details.

This document is to be used by development team, validation and network test teams.

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and explained in below table.

| Convention | Usage |
| ---------- | ----- |
| Host Machines | Machines to be used for Openstack deployment. Openstack node controller, compute, storage and network node will be deployed on these machines. |
| Configuration node | Machine running installation scripts, Ansible, Python, NTP etc. |

### 1.2 Acronyms

The acronyms expanded below are fundamental to the information in this document.

| Acronym | Explanation |
| ------- | ----------- |
| SNAPS | SDN/NFV Application Platform/Stack |
| IP | Internet Protocol |
| COTS | Commercial Off The Shelf |
| OS | OpenStack |
| VLAN | Virtual Local Area Network |

### 1.3 References

[1] OpenStack Installation guide: https://docs.openstack.org/newton/install-guide-ubuntu/

## 2 Environment Prerequisites

### 2.1 Hardware Requirements

The current release of SNAPS-Kolla is tested on the following platform.

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
| OpenStack | Newton |

## 2.3 Pre-requsites Requirements

- Machine running SNAPS-Kolla should have Ubuntu 16.04 Xenial as host OS and should have internet access.
- All host machines should have identical interface names and should have at least 2 interfaces (one for management and one for data).
- All host machines are connected to configuration node (machine running SNAPS-Kolla) and have Internet access connectivity via data interface.

> Note: Configuration node should have http/https and ftp proxy if node is behind corporate firewall. Set the http/https proxy for apt.


## 3 Configuration

### 3.1 deployment.yaml

Configuration file used by SNAPS-Kolla for OpenStack provisioning. Options defined here are used by SNAPS-Kolla to deploy appropriate OpenStack services on host machines and configuring them to be controller, compute or storage nodes.

#### OpenStack:

Parameters defined in this section allows user to specify deployment type for OpenStack services and OpenStack version. Configuration parameter defined in this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| deployement_type | N | OpenStack deployment type, `Devstack` or `Kolla`. |
| git_branch | N | OpenStack release to clone (In current release only Newton is supported so it will be `stable/newton`). |

#### hosts:

This section is used for OpenStack environment planning. Parameters defined here configure host machines as OpenStack controller, compute, storage and network node. Configuration parameter defined in this section are explained below.

| <td colspan=3> **Parameter** | Optionality | Description |
| ---------------------------- | ----------- | ----------- |
| <td colspan=4> host | Define these set of parameter for each host machine (a separate host section should be defined for each host machine). |
|| <td colspan=2> hostname | N | Hostname to be used for the machine. SNAPS-Kolla assigns this hostname to the machine. |
|| <td colspan=3> interfaces | Define these set of parameters for each interface of the host machine. |
||| | ip | N | IP of the primary interface (Management Interface, allocated after OS provisioning). |
||| | name | N | Name of the primary interface. |
||| | type | N | Traffic type (`management`). |
||| | gateway | N | Gateway Ip of the subnet. |
||| | ip | N | IP of the 2nd interface (External Network). |
||| | name | N | Name of 2nd interface. |
||| | type | N | Traffic type (`data`). |
||| | ip | Y | IP of 3rd interface (Tennant Network). |
||| | name | Y | Name of the interface. |
||| | type | Y | Traffic type (`tennant`). |
|| <td colspan=2> node_type | N | List of nodes to be setup on this host machine. User can choose any combination of `controller`, `compute`, `network` and `storage` values. If user wishes to deploy a single node setup, he should use value `all`. |
|| <td colspan=2> service_host | Y | IP of controller machine. Not required if the machine is controller. |
|| <td colspan=2> user | N | User of host machine. |
|| <td colspan=2> password | N | Password for host machine user. |
|| <td colspan=2> isolcpus | Y | CPUs to be pinned for VMs on this host machine. |
|| <td colspan=2> reserved_host_memory_mb | Y | RAM to be reserved for VMs on this host machine. |

#### networks

SNAPS-Kolla uses this section to define external and tennant networks for OpenStack VMs. This section is optional, if user does not provide this section, SNAPS-Kolla will create default network. Configuration parameter defined in this section are explained below.

#### external

| <td colspan=2> **Parameter** | Optionality | Description |
| ---------------------------- | ----------- | ----------- |
| <td colspan=2> gateway | N | Gateway IP for external network. |
| <td colspan=2> ip_pool | | |
||| End | N | Last address for DHCP range. |
||| Start | N | First address for DHCP range. |
| <td colspan=2> Subnet | N | Subnet in CIDR notation. |

#### tenant

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| Subnet | N | Subnet in CIDR notation. |
| subnet_size | N | Size of subnet. |

#### mtu_size

Default MTU size to be used on provider networks.

#### proxies

This section defines environment proxies to be exported on all host machines. Configuration parameter defined in this section are explained below.

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

Defines the additional services to be installed. Allowed values are `magnum`, `telemetry`, `cinder` etc. See sample below:

```
services:
  - magnum
  - tempest
  - ceilometer
  - ceph
  - cinder
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
| count | Y | Total count for the physical volume created. |
| second_storage | Y | Mount point of secondary storage for ceph. |

### 3.2 var.yaml (VLAN Configuration)

Configuration file used by SNAPS-Kolla for VLAN based tenant network provisioning.

#### TASKS

Parameters defined in this section allows user to specify post deployment tasks (VLAN configuration). Configuration parameter defined in this section are explained below:

| <td colspan=3> **Parameter** | Optionality | Description |
| ---------------------------- | ----------- | ----------- |
| <td colspan=3> name | N | Should be `TenantVLAN`. |
| <td colspan=4> host | Define these set of parameter for each host machine (A separate host section should be defined for each host machine). |
|| <td colspan=3> interfaces | Define these set of parameters for each vlan. |
|||| port_name | N | Interface name attached to the vlan. |
|||| vlan_id | N | Vlan id configured at the switch. |
|| <td colspan=2> ip | Y | IP of Management network. |
|| <td colspan=2> username | N | User of host machine. |
|| <td colspan=2> password | N | Password for host machine user. |


### 3.3 var.yaml (MTU settings)

Configuration file used by SNAPS-Kolla for MTU size configuration of physical NICs.

#### TASKS

Parameters defined in this section allows user to specify post deployment tasks ( MTU settings). Configuration parameter defined in this section are explained below.

| <td colspan=3> **Parameter** | Optionality | Description |
| ---------------------------- | ----------- | ----------- |
| <td colspan=3> name | N | Should be `mtu`. |
| <td colspan=4> host | Define these set of parameter for each host machine (A separate host section should be defined for each host machine). |
|| <td colspan=3> interfaces | Define these set of parameters for each interface to be reconfigured for MTU size. |
|||| port_name | N | Interface name attached to the vlan. |
|||| size | N | MTU size. |
|| <td colspan=2> ip | Y | IP of Management network. |
|| <td colspan=2> username | N | User of host machine. |
|| <td colspan=2> password | N | Password for host machine user. |

## 4 Installation Steps

### 4.1 Fresh OpenStack Installation

#### Step 1

Clone/FTP Openstack_Provisioning package on configuration node. All operations of configuration server expect the user should be explicitly switched (using `su root`) to the root user.

#### Step 2

Go to directory `~/snaps-kolla/conf/openstack/kolla`

Modify file `deployment.yaml` for provisioning of OpenStack nodes on cloud cluster host machines (controller node, compute nodes). Modify this file according to your set up environment only (Refer section 3).

#### Step 3

Go to directory `~/snaps-kolla/`

Run `iaas_launch.py` as shown below:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -drs
```

This will install Kolla OpenStack service on host machines. Your OpenStack installation will start and will get completed in ~40 minutes.

### 4.2 VLAN Tennant Network Configuration

#### Step 1

Go to `~/snaps-kolla/utilities/` directory.

Define VLAN ports per host in `var.yaml` file under TenantVLAN task (we can define multiple vlan ports for multiple hosts).

#### Step 2

Run the following command from `~/snaps-kolla/utilities` directory.

```
python utils.py -f var.yaml -tvlan
```

Please configure the switch for tagged vlan ports.

### 4.3 MTU Size Settings for Physical NICs

#### Step 1

Go to `~/snaps-kolla/utilities/` directory.

Define MTU size for NICS per host in `var.yaml` file under mtu task.

#### Step 2

Run the following command from `~/snaps-kolla/utilities` directory:

```
python utils.py -f var.yaml -mtu
```

## 5 Cleanup and Troubleshooting

### 5.1 Fresh Deployment with Existing Docker Repository

If docker based images for OpenStack services are already available run `iaas_launch.py` as shown below:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -d
```

### 5.2 Re-deployment

In case previous deployment attempt has failed or new changes are required (enabling optional services), attempt following steps.

First, Clean up previous OpenStack deployment:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -c
```

Or Clean up previous deployment along with docker repository:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -drc
```

Then, re-install OpenStack. If docker repository exist:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -d
```

Or if docker repository needs to be built:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -drs
```

### 5.3 Cleanup

Clean up previous OpenStack deployment:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -c
```

Clean up previous deployment along with docker repository:

```
sudo python iaas_launch.py -f conf/openstack/kolla/deployment.yaml -drc
```
