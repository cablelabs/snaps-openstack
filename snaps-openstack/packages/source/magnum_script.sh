#!/bin/bash

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

export http_proxy=$1
export https_proxy=$2
git clone https://github.com/openstack/magnum-ui -b stable/newton
cd magnum-ui/
python setup.py sdist
cd magnum_ui/enabled/
cp * /var/lib/kolla/venv/lib/python2.7/site-packages/openstack_dashboard/local/enabled/
cp * /horizon-source/horizon-10.0.3/openstack_dashboard/local/enabled/
cp * /horizon-source/horizon-10.0.3/openstack_dashboard/enabled/
cd ../../
pip install dist/magnum-ui-2.1.2.dev10.tar.gz
service apache2 reload
