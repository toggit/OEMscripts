import csv
import json
import paramiko
import sys
import logging
import os
import errno
import socket

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_secret():
    with open(os.path.join('.secret', 'secret.json')) as json_file:
        loaded_json = json.load(json_file)
    return loaded_json[0]['default']['user'], loaded_json[0]['default']['password']


def print_dict(dict_list=[]):
    for row in dict_list:
        print(row)


def get_dict_from_csv_file(filename, delimiter=',', dir_path='data'):
    logging.debug('try read from file: {0}'.format(filename))
    dict_list = csv.DictReader(
        open(os.path.join(dir_path, filename)), delimiter=delimiter)
    return dict_list


def filter(arr, key, value):
    filter_list = []
    for item in arr:
        if item[key] == value:
            filter_list.append(item)
    return filter_list


def save_outputs(self, output="", filename='output.txt', dir_name='output'):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(os.path.join(dir_path, 'data'), filename)):
        try:
            os.makedirs(os.path.join(dir_path, filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(os.path.join(dir_name, filename), 'w', encoding="utf-8") as f:
        for command in self.commands:
            f.write('\n[input]# {0}\n\n'.format(command['command']))
            f.write(command['output'])


class SshCommand:

    def __init__(self, ip='127.0.0.1', port=22, username='root', password='1234', commands=[]):
        logging.debug('try to connect to: ip={0}, user={1}, pass={2}'.format(
            ip, username, password))
        self._set_connection(
            ip=ip, port=port, username=username, password=password)
        self._set_commands(commands=commands)
        self._print_connection

    def _set_connection(self, ip='127.0.0.1', port=22, username='root', password='1234'):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    def _set_commands(self, commands=[]):
        self.commands = commands

    def _open_connection(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._print_connection()
        try:
            self.ssh_client.connect(
                hostname=self.ip, port=self.port, username=self.username, password=self.password)
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                paramiko.SSHException, socket.error) as e:
            print("Error: couldnot connect to ip: {0}".format(self.ip))
            print(e)

    def _run_commands(self):
        for command in self.commands:
            # print('[input]# {0}'.format(command['command']))
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(
                command['command'])
            byteout = ssh_stdout.read()
            command['output'] = byteout.decode('utf-8')
            # print(command['output'])

    def _get_outputs(self):
        return self.commands

    def _print_connection(self):
        print('try to connect to: ip={0}, user={1}, pass={2}'.format(
              self.ip, self.username, self.password))

    def __del__(self):
        self.ssh_client.close()


def main():
    data_dir = 'data'
    servers_list_filename = "server_list.csv"
    commands_list_filename = "commands_list.csv"

    port = 22
    username, password = load_secret()
    commands = []

    servers = list(get_dict_from_csv_file(
        filename=servers_list_filename, dir_path=data_dir))
    commands = list(get_dict_from_csv_file(
        filename=commands_list_filename, dir_path=data_dir))

    servers = filter(servers, 'Property', 'MNG')

    for srv in servers:
        session = SshCommand(ip=srv['IP'], port=port, username=username,
                             password=password, commands=commands)

        session._open_connection()
        session._run_commands()
        output = session._get_outputs()
        save_outputs(output,
                     '{0}-output.txt'.format(srv['Component']))


if __name__ == '__main__':
    main()
