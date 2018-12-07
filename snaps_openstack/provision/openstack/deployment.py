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

import logging
import os
import sys

from snaps_openstack.provision.openstack.plugin.kolla_impl import kolla_utils

logger = logging.getLogger('deploy_infra')


def deploy_infra(conf, flag):
    if __load(conf, flag):
        logger.info('Openstack operation is unsuccessful')
    else:
        logger.info('Openstack operation is successful')


def __load(data, operation):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    plugin_path = dir_path + "/plugin/"
    logger.info(plugin_path)
    sys.path.append(plugin_path)
    if operation is "clean" or operation is "cleanregistry":
        ret = kolla_utils.clean_up(data, operation)
    if operation is "upgrade" or operation is "downgrade":
        ret = kolla_utils.upgrade_downgrade_cluster(data, operation)
    else:
        ret = kolla_utils.main(data, operation)

    return ret
