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
import sys
import os

from snaps_openstack.common.utils import file_utils
from snaps_openstack.provision.openstack.deployment import deploy_infra

sys.path.append("common/utils")
__author__ = '_ARICENT'

logger = logging.getLogger('launch_provisioning')

ARG_NOT_SET = "argument not set"


def __manage_operation(config, operation):
    """
     This will launch the provisioning of openstack setup on the cluster node
     which are defined in the conf/openstack/devstack/deployment.yaml.
     :param config: This configuration data extracted from the provided yaml
                    file.
    """

    if config:
        config_dict = {}
        if config.get('openstack'):
            logger.info("Your deployement model is :")
            logger.info(config_dict.get('deployement_type'))

            logger.info(
                "########################### Yaml Configuration##############")
            logger.info(config)
            logger.info(
                "############################################################")
            logger.info("Read & Validate functionality for Devstack")
            deploy_infra(config, operation)
        else:
            logger.error("Configuration Error ")


def main(arguments):
    """
     This will launch the provisioning of Bare metat & IaaS.
     There is pxe based configuration defined to provision the bare metal.
     For IaaS provisioning different deployment models are supported.
     Relevant conf files related to PXE based Hw provisioning & Openstack based
     IaaS must be present in ./conf folder.
     :param arguments: the command line arguments
     :return: To the OS
    """

    log_level = logging.INFO
    if arguments.log_level != 'INFO':
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    logger.info('Launching Operation Starts ........')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    export_path = dir_path + "/"
    os.environ['CWD_IAAS'] = export_path
    print("==================Current Exported Relevant Path==================")
    logger.info(export_path)

    config = file_utils.read_yaml(arguments.config)
    logger.info('Read configuration file - ' + arguments.config)

    if arguments.deploy is not ARG_NOT_SET:
        __manage_operation(config, "deploy")
    if arguments.dreg is not ARG_NOT_SET:
        __manage_operation(config, "deployregistry")
    if arguments.dregclean is not ARG_NOT_SET:
        logger.info("Cleaning up along with registry")
        logger.info(arguments.dregclean)

        __manage_operation(config, "cleanregistry")
        # Functions to read yml for IaaS Openstack environment
    if arguments.clean is not ARG_NOT_SET:
        __manage_operation(config, "clean")

    logger.info('Completed opeartion successfully')


if __name__ == '__main__':
    # To ensure any files referenced via a relative path will begin from the
    # directory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--deploy', dest='deploy', nargs='?', default=ARG_NOT_SET,
        help='When used, deployment and provisioning of openstack will be '
             'started')
    parser.add_argument(
        '-c', '--clean', dest='clean', nargs='?', default=ARG_NOT_SET,
        help='When used, the openstack environment will be removed')
    parser.add_argument(
        '-f', '--file', dest='config', required=True,
        help='The configuration file in YAML format - REQUIRED',
        metavar="FILE")
    parser.add_argument(
        '-l', '--log-level', dest='log_level', default='INFO',
        help='Logging Level (INFO|DEBUG)')
    parser.add_argument(
        '-drs', '--dreg', dest='dreg', nargs='?', default=ARG_NOT_SET,
        help='When used, to set up kolla registry along with deployment')
    parser.add_argument(
        '-drc', '--dregc', dest='dregclean', nargs='?', default=ARG_NOT_SET,
        help='When used, to cleanup up kolla registry')
    args = parser.parse_args()

    if (args.dreg is ARG_NOT_SET and args.dregclean is ARG_NOT_SET
            and args.deploy is ARG_NOT_SET and args.clean is ARG_NOT_SET):
        logger.info(
            'Must enter either -d for deploy IaaS or -c for cleaning up and '
            'environment or -drc to cleanup registry or -drs to setup '
            'registry')
        exit(1)
    if args.deploy is not ARG_NOT_SET and args.clean is not ARG_NOT_SET:
        logger.info('Cannot enter both options -d/--deploy and -c/--clean')
        exit(1)
    if args.deploy is not ARG_NOT_SET and args.config is ARG_NOT_SET:
        logger.info(
            'Cannot start deploy operation without configuration. '
            'Choose the option -f/--file')
        exit(1)
    if args.deploy is ARG_NOT_SET and args.config is ARG_NOT_SET:
        logger.info(
            'Cannot start any deploy iaas operation without both -d/--deploy '
            'and -f/--file')
        exit(1)

    main(args)
