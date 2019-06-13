
# Continuous Integration ReadMe

## 1 Introduction

This document serves as a guide for developers to test this project
in a Continuous Integration (CI) environment.  It can also be used
to evaluate this project for new users.

To test the installation process, the scripts under the ci/baremetal directory
can create compute, networking and storage resources to run OpenStack and test advanced features of OpenStack - MTU, VLAN, SRIOV, DPDK


### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and
explained in below table.

| Convention | Usage |
| ---------- | ----- |
| CI Server | This is the physical were we run the CI script. The CI server will connect to an OpenStack instance to create the environment|
| Build Server | The physical machine which will install snaps-openstack |
| Controller | The physical server which will have snaps-openstack installed on it. |
| Compute    | The physical server which will have snaps-openstack compute containers installed on it.|
### 1.2 Acronyms

The acronyms expanded below are fundamental to the information in this
document.

| Acronym | Explanation |
| ------- | ----------- |
| CI | Continuous Integratoin |

### 1.3 References

[1] OpenStack Installation guide:
https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html

## 2 CI server setup

1. Download and set branch of snaps-openstack to test
```
mkdir /home/ubuntu/test-snaps-openstack
cd /home/ubuntu/test-snaps-openstack
git clone https://github.com/cablelabs/snaps-openstack.git
cd /home/ubuntu/test-snaps-openstack/snaps-openstack
git checkout <branch>
```

2. Download and install baremetal CICD code. 
```
cd /home/ubuntu
git clone https://github.com/cablelabs/snaps-openstack.git
cd /home/ubuntu/snaps-openstack/ci/baremetal
sudo apt-get update
sudo pip install ansible==2.4.0.0
```
3.  Configure the environment file.
This file will provide information about the configuration and the
host machines on which snaps-openstack will be installed on.
lab.yaml
```
---
workspace: project

proxy_host: 165.225.104.34
proxy_port: 80

pxe_server:
   ip: 172.16.139.36
   user: root
   pass: ChangeMe
   interface: enp2s0

mgmt_prefix: 172.16.139
tenant_prefix: 172.16.140
data_prefix: 172.16.141
ipmi_prefix: 172.16.141

compute:
   ipmi_user: admin
   ipmi_pass: abc123
   mac: d0:94:66:35:e3:16

controller:
   ipmi_user: admin
   ipmi_pass: abc123
   mac: d0:94:66:35:e5:52

mtu:
   default: 1500
   vxlan: 3000

vlan:
   min_vlan_id: 1001
   max_vlan_id: 1002
   interface: eno3

sriov:
   interface: enp4s0f1

```
4. Launch the test

```
sudo ansible-playbook playbooks/main.yaml --extra-vars="@lab.yaml"
```
