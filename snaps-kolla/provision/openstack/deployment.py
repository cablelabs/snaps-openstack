# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL. and Cable Television Laboratories, Inc.
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

from plugin_loader import PluginLoader
import logging

#data= {"1":"abc", "def":"123", "2":"ghy"}
logger = logging.getLogger('deploy_infra')

def deploy_infra (conf, flag):

     deploy=PluginLoader()
     ret=False
     deployment_type = conf.get('openstack').get('deployement_type')
     if deploy.load(deployment_type, conf, flag) :
         logger.info('Openstack operation is unsuccessfull')
         ret=False
     else:
         logger.info('Openstack operation is successfull')
         ret=True
