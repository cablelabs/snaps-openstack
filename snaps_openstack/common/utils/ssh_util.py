import logging
import paramiko

logger = logging.getLogger('ssh_utils')


def host_command_execution(ip_addr, username, password, cmd=None, port=22):
    global logger
    current_log_level = logger.getEffectiveLevel()
    logger = paramiko.util.logging.getLogger()
    logger.setLevel(logging.CRITICAL)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_addr, port, username, password)
    logger.setLevel(logging.getLevelName(current_log_level))
    if not cmd:
        return True

    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout._set_mode('b')
    outlines = stdout.readlines()
    ssh.close()

    return [i.strip() for i in outlines]
