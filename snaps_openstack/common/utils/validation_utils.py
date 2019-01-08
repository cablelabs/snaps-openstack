import logging
import subprocess
import ipaddress
import ssh_util

logger = logging.getLogger('validation_utils')


class ValidationException(Exception):
    """
    Exception to raise when there are issues with the configuration
    """


def validate_router_id(value, name):
    """
    Validates virtual router ID
    """
    if not (isinstance(value, int) or (isinstance(value, str) and value.isdigit())):
        raise ValidationException(
            "Validation failed for " + str(name) + " parameter with " + str(value) + \
            " value\n" + str(name) + " can only have integer value")

    if int(value) < 1 or int(value) > 255:
        raise ValidationException("Virtual router ID can only have value between 1 and 255")
    return True


def validate_isolated_cpu(value, name):
    """
    Validates isolated CPU
    """
    import re
    if not isinstance(value, str):
        raise ValidationException(
            "%s field having %s isolated CPUs is not a valid string." % (name, value))
        regexp = re.compile(r'^\d+([-|,]\d+)*$')
        if not regexp.search(value):
            raise ValidationException(
                "%s field having %s isolated CPUs does not meet prescribed format\
            correct format is range (e.g.start cpu - end cpu) \
            or specific cpus (1,2,3 etc)." % (name, value))
    return True


def validate_optional_ipaddr(ipaddr, name):
    """
    Verifies that the IP address can either be null or of valid format
    """
    if not ipaddr:
        return True
    return validate_ipaddr(ipaddr, name)


def validate_subnet(subnet, name):
    """
    Verifies that IP address is of valid format
    """
    try:
        ipaddress.ip_network(unicode(subnet), False)
    except Exception, e:
        raise ValidationException(
            "%s field having Subnet %s. %s" % (name, subnet, str(e)))
    return True


def validate_ipaddr(ipaddr, name):
    """
    Verifies that IP address is of valid format
    """
    try:
        ipaddress.ip_address(unicode(ipaddr))
    except Exception, e:
        raise ValidationException(
            "%s field having IP address %s. %s" % (name, ipaddr, str(e)))
    return True


def validate_tags_input_file(name, schema, dep_contents):
    """
    Verifies the deployment file against the mentioned schema
    """
    if isinstance(schema, dict) and isinstance(dep_contents, dict):
        # schema is a dict of types or other dicts
        for k in dep_contents:
            if k in schema:
                if not validate_tags_input_file(k, schema[k].get("type"), dep_contents[k]):
                    raise ValidationException(
                        "Validation failed, " + str(name) + "/" + k + " parameter doesn't exists")
            else:
                raise ValidationException(
                    "Validation failed, " + str(name) + "/" + k + " parameter doesn't exists")
        return True

    if isinstance(schema, list) and isinstance(dep_contents, list):
        # schema is list in the form [type or dict]
        for i in dep_contents:
            if not validate_tags_input_file(name, schema[0], i):
                raise ValidationException(
                    "Validation failed, " + str(name) + "/" + i + " parameter doesn't exists")
        return True

    if isinstance(schema, type):
        # schema is the type of dep_contents
        if isinstance(dep_contents, schema):
            return True
        else:
            raise ValidationException(
                "Validation failed, " + str(name) + "/" + str(dep_contents) + " parameter doesn't exists")
    return True


def validate_input_file(name, schema, dep_contents):
    """
    Verifies the deployment file against the mentioned schema
    """
    if isinstance(schema, dict) and isinstance(dep_contents, dict):
        # schema is a dict of types or other dicts
        for k in schema:
            if not schema[k].get("required") and not dep_contents.has_key(k):
                continue
            if k in dep_contents:
                if not validate_input_file(k, schema[k].get("type"), dep_contents[k]):
                    raise ValidationException(
                        "Validation failed for " + str(name) + " parameter with " + k + " value")
            else:
                raise ValidationException(
                    "Validation failed for " + str(name) + " parameter with " + k + " value")
        return True

    if isinstance(schema, list) and isinstance(dep_contents, list):
        # schema is list in the form [type or dict]
        for i in dep_contents:
            if not validate_input_file(name, schema[0], i):
                raise ValidationException(
                    "Validation failed for " + str(name) + " parameter with " + i + " value")
        return True

    if isinstance(schema, type):
        # schema is the type of dep_contents
        if isinstance(dep_contents, schema):
            return True
        else:
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + \
                str(dep_contents) + " value")

    if hasattr(schema, '__call__'):
        return schema(dep_contents, name)

    if isinstance(schema, list) and isinstance(dep_contents, str):
        if dep_contents in schema:
            return True
        else:
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
                " value\n" + str(name) + " can only have value from " + str(schema))

    if schema == "str with no null":
        if not (isinstance(dep_contents, str) and dep_contents):
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
                " value\n" + str(name) + " can only have only string")
        return True

    if schema == "str or null":
        if not (dep_contents is None or isinstance(dep_contents, str)):
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
                " value\n" + str(name) + " can only have either string or null value")
        return True

    if schema == "int or strOfInt":
        if not (isinstance(dep_contents, int) or (isinstance(dep_contents, str) \
                                                          and dep_contents.isdigit())):
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
                " value\n" + str(name) + " can only have integer value")
        return True

    if schema == "array_of_string or none":
        if dep_contents is None or all(isinstance(k, str) for k in dep_contents):
            return True
        else:
            raise ValidationException(
                "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
                " value\n" + str(name) + " can only have array of strings or null value")

    # schema is neither a dict, nor list, not type
    raise ValidationException(
        "Validation failed for " + str(name) + " parameter with " + str(dep_contents) + \
        " value\n" + str(name) + " can only have value from " + str(schema) + " type")


def validate_hostname(deployment_content):
    """
    Validates OpenStack node hostname configuration
    """
    hostname_list = [host_name.get('host').get('hostname')
                     for host_name in deployment_content.get('hosts')]
    if len(hostname_list) - len(set(hostname_list)):
        raise ValidationException("Dublicate hostname found in deployment")


def validate_service(deployment_content):
    """
    Validates OpenStack service configuration
    """
    if deployment_content.has_key('services'):
        logger.info('Service level validation starts')
        validate_ceph(deployment_content)
        validate_sriov(deployment_content)
        validate_dpdk(deployment_content)


def validate_ceph(deployment_content):
    """
    Validates ceph related configuration
    """
    logger.info('starting ceph validation')
    if 'ceph' in deployment_content.get('services') and \
                    'cinder' not in deployment_content.get('services'):
        raise ValidationException("Error: Ceph is enabled in services but "
                                  "cinder not, both should be present")
    if 'cinder' in deployment_content.get('services') and \
                    'ceph' not in deployment_content.get('services'):
        raise ValidationException("Error: Cinder is enabled in services but "
                                  "ceph not, both should be present")
    if all(k in deployment_content.get('services') for k in ['ceph', 'cinder']):
        if not deployment_content.get('kolla').has_key('base_size'):
            raise ValidationException(
                "Ceph/Cinder is enable but base_size is not present")
        if not deployment_content.get('kolla').has_key('count'):
            raise ValidationException(
                "Ceph/Cinder is enable but count is not present")

        storge_conf_flag = 0
        for host in deployment_content.get('hosts'):
            if 'storage' in host.get('host').get('node_type') and \
                    host.get('host').get('second_storage'):
                ip_addr = [interface_element.get('ip')
                           for interface_element in host.get('host').get('interfaces') \
                           if interface_element.get('type') == 'management']
                username = host.get('host').get('user')
                password = host.get('host').get('password')
                for storage in host.get('host').get('second_storage'):
                    cmd = 'fdisk -l | grep ' + storage
                    res = ssh_util.host_command_execution(ip_addr[0], username, password, cmd)
                    if not any(storage in mystring for mystring in res):
                        raise ValidationException("Storage %s not present on host %s " %
                                                  (storage, host.get('host').get('hostname')))
                storge_conf_flag = storge_conf_flag + 1
            if ('storage' not in host.get('host').get('node_type') and \
                        host.get('host').get('second_storage')) or \
                    ('storage' in host.get('host').get('node_type') and \
                             not host.get('host').get('second_storage')):
                raise ValidationException("Error: When ceph is enabled Storage node_type "
                                          "and second_storage both should be present")
        if not storge_conf_flag:
            raise ValidationException("Error: At least one node should be copnfigured for storage ")

    if all(k not in deployment_content.get('services') for k in ['ceph', 'cinder']):
        for host in deployment_content.get('hosts'):
            if 'storage' in host.get('host').get('node_type') or \
                            'second_storage' in host.get('host'):
                raise ValidationException("When ceph and cinder are disabled, "
                                          "second_storage and node_type as storage"
                                          " should not be present")


def validate_dpdk(deployment_content):
    """
    Validates DPDK related configuration
    """
    logger.info('starting dpdk validation')
    if 'dpdk' in deployment_content.get('services'):
        for host in deployment_content.get('hosts'):
            for interface_element in host.get('host').get('interfaces'):
                if interface_element.get('type') == 'data':
                    if interface_element.get('ip') is None:
                        raise ValidationException("DPDK needs valid ip for %s host"
                                                  % host.get('host').get('hostname'))


def validate_sriov(deployment_content):
    """
    Validates SRIOV related configuration
    """
    logger.info('starting sriov validation')
    sriov_count = 0
    ip_addr = '127.0.0.0'
    if 'sriov' in deployment_content.get('services'):
        for host in deployment_content.get('hosts'):
            if 'compute' in host.get('host').get('node_type'):
                ip_addr = [interface_element.get('ip')
                           for interface_element in host.get('host').get('interfaces') \
                           if interface_element.get('type') == 'management']
                if host.get('host').get('sriov_interface') != None:
                    username = host.get('host').get('user')
                    password = host.get('host').get('password')
                    for intf in host.get('host').get('sriov_interface'):
                        cmd = 'ifconfig ' + intf
                        res = ssh_util.host_command_execution(ip_addr[0], username, password, cmd)
                        if not res:
                            raise ValidationException("Error:Provided interface %s is not correct" %
                                                      (host.get('host').get('sriov_interface')))
                        cmd = 'ifconfig' + ' ' + intf + ' ' + 'up'
                        res = ssh_util.host_command_execution(ip_addr[0], username, password, cmd)

                        cmd = 'ethtool ' + intf + '| grep \"Link detected:\" |awk \'{print $3}\''
                        res = ssh_util.host_command_execution(ip_addr[0], username, password, cmd)
                        if 'yes' not in res:
                            raise ValidationException("Error:Provided interface "
                                                      "is configured but not UP")
                    sriov_count += 1
        if not sriov_count:
            raise ValidationException("Sriov is configured at service but is "
                                      "not present in any of the compute hosts")
    else:
        for host in deployment_content.get('hosts'):
            if 'compute' in host.get('host').get('node_type'):
                if host.get('host').get('sriov_interface') != None:
                    raise ValidationException(
                        "Sriov is not configured in the services, but "
                        "is present in the compute %s hosts" % (host.get('host').get('hostname')))



def validate_network_range(deployment_content):
    """
    Validates that start IP should be less than end IP
    """
    logger.info('starting start and end IP validation')
    start_ip = deployment_content.get('networks').get('external').get('ip_pool').get('start')
    end_ip = deployment_content.get('networks').get('external').get('ip_pool').get('end')
    gateway_ip = deployment_content.get('networks').get('external').get('gateway')
    subnet_addr = deployment_content.get('networks').get('external').get('subnet')

    if ipaddress.ip_address(unicode(end_ip)) < ipaddress.ip_address(unicode(start_ip)):
        raise ValidationException("End IP(%s) is less than start IP(%s)" % (end_ip, start_ip))

    for ip_addr in [start_ip, end_ip, gateway_ip]:
        if ipaddress.ip_address(unicode(ip_addr)) not in ipaddress.ip_network(unicode(subnet_addr)):
            raise ValidationException('IP address %s is not within %s subnet range'
                                      % (ip_addr, subnet_addr))


def validate_node_type(deployment_content):
    """
    Validates that the configuration contains controller, network and compute nodes.
    """
    logger.info('starting node type validation')
    node_types = []
    controller_cnt = 0
    compute_cnt = 0
    network_cnt = 0
    dset_node_type = [{'compute', 'network', 'controller'}, {'compute', 'network', 'controller', 'storage'}, \
                      {'controller', 'network'}, {'controller', 'network', 'storage'}, {'compute', 'storage'},
                      {'compute'}]
    if len(deployment_content.get('hosts')) != 1:
        for host in deployment_content.get('hosts'):
            if set(host.get('host').get('node_type')) not in dset_node_type:
                raise ValidationException('Invalid node type set %s  '
                                          % (set(host.get('host').get('node_type'))))
            if 'controller' in set(host.get('host').get('node_type')):
                controller_cnt = controller_cnt + 1
            if 'compute' in set(host.get('host').get('node_type')):
                compute_cnt = controller_cnt + 1
            if 'network' in set(host.get('host').get('node_type')):
                network_cnt = controller_cnt + 1
    if controller_cnt < 1 or controller_cnt > 2:
        raise ValidationException("Number of Nodes with controller type "
                                  "should be either one or two")
    if network_cnt < 1:
        raise ValidationException("Atleast one node should be configured as a network node")
    if compute_cnt < 1:
        raise ValidationException("Atleast one node should be configured as a compute node")


def validate_mtu_sizes(deployment_content):
    """
    Validates that the vxlan MTU size is less than default MTU size
    """
    logger.info('starting MTU size validation')
    if deployment_content.get('networks').get('mtu_size'):
        default_mtu = deployment_content.get('networks').get('mtu_size').get('default')
        vxlan_mtu = deployment_content.get('networks').get('mtu_size').get('vxlan')
        if default_mtu and not vxlan_mtu:
            raise ValidationException(
                "Default MTU is defined but VXLAN MTU is not defined")
        if not default_mtu and vxlan_mtu:
            raise ValidationException(
                "Default MTU is not defined but VXLAN MTU is defined")

        if default_mtu < (vxlan_mtu + 50):
            raise ValidationException(
                "Default MTU must be atleast 50 more than VXLAN MTU")


def validate_interface_data(deployment_content):
    """
    Validates interface related contents of host related contents
    """
    logger.info('starting interface related validation')
    interface_array = []
    management_ip = ''
    interface_count = 0
    for host in deployment_content.get('hosts'):
        interface_count = len(host.get('host').get('interfaces'))
        data_interface = 0
        management_interface = 0

        if interface_count < 2 or interface_count > 3:
            raise ValidationException(
                "Total number interfaces present for %s hosts is %d which is incorrect" %
                (host.get('host').get('hostname'), interface_count))
        for interface_element in host.get('host').get('interfaces'):
            if interface_element.get('type') == 'data':
                data_interface += 1

                if not interface_element.has_key('gateway'):
                    raise ValidationException(
                        "Data interface of %s host does not contain gateway IP"
                        % host.get('host').get('hostname'))
                validate_ipaddr(interface_element.get('gateway'), 'gateway')
                cmd = 'ifconfig ' + interface_element.get('name')
                if management_ip != '':
                    res = ssh_util.host_command_execution(
                        management_ip,
                        host.get('host').get('username'),
                        host.get('host').get('password'), cmd)
                    if not res:
                        raise ValidationException("Error:Provided interface $s is not correct" %
                                                  (interface_element.get('name')))
            elif interface_element.get('type') == 'management':
                if interface_element.has_key('gateway'):
                    raise ValidationException(
                        "Other than Data interface of %s host does contain gateway IP"
                        % host.get('host').get('hostname'))
                validate_ipaddr(interface_element.get('ip'), 'ip')
                management_ip = interface_element.get('ip')
                cmd = "ssh-keygen -f /root/.ssh/known_hosts -R " + interface_element.get('ip')
                subprocess.call(cmd, shell=True)
                management_interface += 1
                logger.info("Trying to connect on %s", interface_element.get('ip'))
                ssh_util.host_command_execution(interface_element.get('ip'),
                                                host.get('host').get('username'),
                                                host.get('host').get('password'))
                logger.info("Connection successful on %s", interface_element.get('ip'))

                cmd = 'ifconfig ' + interface_element.get('name')
                res = ssh_util.host_command_execution(interface_element.get('ip'),
                                                      host.get('host').get('username'),
                                                      host.get('host').get('password'), cmd)
                if not res:
                    raise ValidationException("Error:Provided interface $s is not correct" %
                                              (interface_element.get('name')))
            elif interface_element.get('type') == 'tenant':
                logger.info("tenant interface")
            else:
                logger.info("No valid interface")
        if data_interface != 1:
            raise ValidationException(
                "%s hosts should have only one data interface, whereas %d interfaces present" %
                (host.get('host').get('hostname'), data_interface))
        if management_interface != 1:
            raise ValidationException(
                "%s hosts should have only one management interface, whereas %d "
                "interfaces present" % (host.get('host').get('hostname'), management_interface))
        interface_array.append(interface_count)
    if len(set(interface_array)) != 1:
        raise ValidationException("All hosts doesnt have same number of iterfaces. Number of "
                                  "interface in all the hosts is %s" % str(interface_array))
    all_ip_list = [j.get('ip')
                   for i in deployment_content.get('hosts')
                   for j in i.get('host').get('interfaces') if j.get('ip')]
    if list(set([k for k in all_ip_list if all_ip_list.count(k) > 1])):
        raise ValidationException("%s are the duplicate IPs configured in the deployment file" %
                                  list(set([k for k in all_ip_list if all_ip_list.count(k) > 1])))

    intf_name_list = {j.get('name'): j.get('type')
                      for i in deployment_content.get('hosts')
                      for j in i.get('host').get('interfaces')}
    if interface_count != len(intf_name_list):
        raise ValidationException("Interface name are not configured correctly")


def validate_deployment_content(deployment_content):
    """
    Entry point for verifying deployment file
    """
    deployment_schema = {
        'openstack': {
            'required': True,
            'type': {
                'versioning': {
                'required': True,
                    'type': {
                            'release': {'required' : True, 'type': "str with no null"},
                            'image': {'required' : True,'type' : [
                                                  'pull','built']},
                            'repo': {'required' : True , 'type': "str with no null"},
                            'repo_tag': {'required' : True , 'type': "str with no null"}, 
                            },
                 },
                'hosts': {
                    'required': True,
                    'type': [{
                        'host': {
                            'required': True,
                            'type': {
                                'hostname': {'required': True, 'type': "str with no null"},
                                'interfaces': {
                                    'required': True,
                                    'type': [{
                                        'ip': {'required': True, 'type': validate_optional_ipaddr},
                                        'gateway': {'required': False, 'type': validate_optional_ipaddr},
                                        'name': {'required': True, 'type': "str with no null"},
                                        "type": {'required': True, 'type': [
                                            'management', 'tenant', 'data']},
                                    }],
                                },
                                'isolcpus': {'required': False, 'type': validate_isolated_cpu},
                                'reserved_host_memory_mb': {
                                    'required': True, 'type': "str or null"},
                                "node_type": {'required': True, 'type': [
                                    ['network', 'controller', 'storage', 'compute']]},
                                "second_storage": {'required': False, 'type': [str]},
                                'sriov_interface': {'required': False,
                                                    'type': "array_of_string or none"},
                                'password': {'required': True, 'type': "str with no null"},
                                'service_host': {'required': False, 'type': validate_optional_ipaddr},
                                'user': {'required': True, 'type': "str with no null"},
                            }
                        }
                    }]
                },

                "networks": {
                    'required': True,
                    'type': {
                        "external": {
                            'required': True,
                            'type': {
                                "gateway": {'required': True, 'type': validate_ipaddr},
                                "ip_pool": {
                                    'required': True,
                                    'type': {
                                        "end": {'required': True, 'type': validate_ipaddr},
                                        "start": {'required': True, 'type': validate_ipaddr},
                                    },
                                },
                                "subnet": {'required': True, 'type': validate_subnet}
                            },
                        },
                        "tenant": {
                            'required': False,
                            'type': {
                                "subnet": {'required': False, 'type': validate_subnet},
                                "subnet_size": {'required': False, 'type': "str or null"},
                            }
                        },
                        "mtu_size": {
                            'required': False,
                            'type': {
                                "default": {'required': False, 'type': int},
                                "vxlan": {'required': False, 'type': int}
                            }
                        }
                    },
                },

                "proxies": {
                    'required': False,
                    'type': {
                        "ftp_proxy": {'required': True, 'type': str},
                        "http_proxy": {'required': True, 'type': str},
                        "https_proxy": {'required': True, 'type': str},
                        "no_proxy": {'required': True, 'type': str}
                    }
                },
                "service_password": {'required': False, 'type': str},
                "services": {
                    'required': False, 'type': [
                        ["cinder", "ceph", "magnum", "tempest", "ceilometer", "tacker",
                         "sriov", "pci-passthrough", 'designate', 'dpdk', 'sfc']]},

                "kolla": {
                    'required': True,
                    'type': {
                        "base_distro": {'required': True, 'type': ["ubuntu"]},
                        "install_type": {'required': True, 'type': ["source", "binary"]},
                        "keepalived_virtual_router_id": {
                            'required': True, 'type': validate_router_id},
                        "internal_vip_address": {'required': False, 'type': validate_ipaddr},
                        "kolla_registry": {'required': True, 'type': validate_ipaddr},
                        "kolla_registry_port": {'required': True, 'type': "int or strOfInt"},
                        "external_vip_address": {'required': False, 'type': validate_ipaddr},
                        "base_size": {'required': False, 'type': "int or strOfInt"},
                        "count": {'required': False, 'type': "int or strOfInt"},
                    }
                }
            }
        }
    }

    try:
        validate_input_file('openstack', deployment_schema, deployment_content)
        validate_tags_input_file('openstack', deployment_schema, deployment_content)
        validate_hostname(deployment_content.get('openstack'))
        validate_interface_data(deployment_content.get('openstack'))
        validate_service(deployment_content.get('openstack'))
        validate_network_range(deployment_content.get('openstack'))
        validate_node_type(deployment_content.get('openstack'))
        validate_mtu_sizes(deployment_content.get('openstack'))
    except Exception as e:
        logger.info("Exception received while validating the file - %s\n", str(e))
        exit(1)
    return True
