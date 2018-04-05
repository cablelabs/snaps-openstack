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

# This script is responsible for deploying Aricent_Iaas environments and
# Openstack Services
import argparse
import logging
import os

from snaps_openstack.common.utils import file_utils
from snaps_openstack.utilities import network_utils

__author__ = '_ARICENT'

ARG_NOT_SET = "argument not set"

logger = logging.getLogger('vlan_setup')


def __main(arguments):
    """
    Configures tagged VLANs or MTUs
    :param arguments: the command line args from main
    TODO/FIXME - send in parsed arguments here, not the ones from the
    interpreter
    """
    log_level = logging.INFO
    if arguments.log_level != 'INFO':
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    logger.info('Launching Utils Operation ........')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    export_path = dir_path + "/"
    os.environ['CWD_IAAS'] = export_path
    print("==================Current Exported Relevant Path==================")
    logger.info(export_path)

    config = file_utils.read_yaml(arguments.config)
    logger.info('Read configuration file - ' + arguments.config)
    try:
        if arguments.tenant_vlan is not ARG_NOT_SET:
            for task in config.get("TASKS"):
                if task.get("name") == "TenantVLAN":
                    logger.info("Performing Task " + task.get(
                        'name') + " with arguments")
                    logger.info("--tenant_vlan")
                    network_utils.add_ansible_hosts(task.get("HOSTS"))
                    ret = network_utils.tenant_vlan(task)
                    if ret == 0:
                        logger.info('Completed opeartion successfully')
                    else:
                        logger.info('Error while performing operation')
        if arguments.mtu is not ARG_NOT_SET:
            for task in config.get("TASKS"):
                if task.get("name") == "mtu":
                    logger.info("Performing Task " + task.get(
                        'name') + " with arguments")
                    logger.info("--mtu")
                    network_utils.add_ansible_hosts(task.get("HOSTS"))
                    ret = network_utils.mtu(task)
                    if ret == 0:
                        logger.info('Completed operation successfully')
                    else:
                        logger.info('Error while performing operation')

    except Exception as e:
        logger.error(
            'Unexpected error deploying environment. Rolling back due to - %s',
            e)
        raise e


if __name__ == '__main__':
    # To ensure any files referenced via a relative path will begin from the
    # directory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', dest='config', required=True,
        help='The configuration file in YAML format - REQUIRED',
        metavar="FILE")
    parser.add_argument(
        '-l', '--log-level', dest='log_level', default='INFO',
        help='Logging Level (INFO|DEBUG)')
    parser.add_argument(
        '-tvlan', '--tenant_vlan', dest='tenant_vlan', nargs='?',
        default=ARG_NOT_SET,
        help='When used, deployment and provisioning of openstack will be '
             'started')
    parser.add_argument(
        '-mtu', '--mtu', dest='mtu', nargs='?', default=ARG_NOT_SET,
        help='When used, sets the mtu size on nic')
    args = parser.parse_args()

    if (args.tenant_vlan is ARG_NOT_SET
            and args.config is ARG_NOT_SET):
        logger.info(
            'Must enter -tvlan for configuring vlan based tenant networks')
        exit(1)

    __main(args)