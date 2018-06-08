
# Continuous Integration ReadMe

## 1 Introduction

This document serves as a guide for developers to test this project
in a Continuous Integration (CI) environment.  It can also be used
to evaluate this project for new users.

To test the installation process, the scripts under the ci directory
can create compute, networking and storage resources to run OpenStack
inside an open stack environment.  Most features are available
in this nested environment, but performance will suffer.

This will enable more testing and development to occur than would be
supported on available physical hardware.

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and
explained in below table.

| Convention | Usage |
| ---------- | ----- |
| CI Server | This is the physical or virtual server were we run the CI script. The CI server will connect to an OpenStack instance to create the environment|
| Build Server | The VM which will install snaps-openstack |
| Controller | The VM which will have snaps-openstack installed on it. |
| Compute    | The VM which will have snaps-openstack compute containers installed on it.|
### 1.2 Acronyms

The acronyms expanded below are fundamental to the information in this
document.

| Acronym | Explanation |
| ------- | ----------- |
| CI | Continuous Integratoin |
| VM | Virtual Machine |

### 1.3 References

[1] OpenStack Installation guide:
https://docs.openstack.org/kolla-ansible/latest/user/quickstart.html

## 2 CI server setup

1. Download and install snaps-oo.
```
git clone https://gerrit.opnfv.org/gerrit/snaps
sudo apt update
sudo apt install python git python2.7-dev libssl-dev python-pip
sudo pip install -e snaps/snaps
```

2. Download and set branch of snaps-openstack to test
```
git clone https://github.com/cablelabs/snaps-openstack.git
cd snaps-openstack
git checkout <branch>
```
3.  Configure the environment file.
This file will provide information about the configuration and the
OpenStack isntance which snaps-openstack will be installed on.
lab3.yaml
```
---
build_id: ci-hack

admin_user: admin
admin_proj: admin
admin_pass: foobar
auth_url: http://10.197.113.30:5000
id_api_version: 3
proxy_host:
proxy_port:
ssh_proxy_cmd:

os_user_pass: password

ext_net: external
ext_subnet: external-net

src_copy_dir: /tmp

ctrl_ip_prfx: 10.0.0
admin_ip_prfx: 10.1.0
admin_iface: ens3
priv_ip_prfx: 10.1.1
priv_iface: ens4
pub_ip_prfx: 10.1.2
pub_iface: ens5

build_kp_pub_path: /tmp/build-kp-lab3.pub
build_kp_priv_path: /tmp/build-kp-lab3

deployment_yaml_target_path: /tmp/deployment.yaml

node_host_password: Pa$$w0rd

local_snaps_openstack_dir: /home/ubuntu/snaps-openstack
```
4. Launch the test
This is best to do in a screen session and redirect the output.
It will take about an hour to run.
```
cd snaps/examples
python ./launch.py -t /home/ubuntu/snaps-openstack/ci/snaps/snaps_os_tmplt.yaml \
-e lab3.yaml -d
```
5. Clean the environment
This will remove the account, VMs, netwoks and storage that was created
in the install.
```
python ./launch.py -t /home/ubuntu/snaps-openstack/ci/snaps/snaps_os_tmplt.yaml \
-e lab3.yaml -c
```
