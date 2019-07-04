import json
import socket
import subprocess
import sys


def check_eui64(eui64: str) -> bool:
    process = subprocess.Popen(['rake', 'get_eui64', eui64])
    return eui64 in process.stdout.readlines()[0]


DNSMASQ_MSG_PARSE_ORDER = ['sc-name', 'process', 'mac', 'ip', 'name']
SERVER_ADDRESS = '/etc/shg/sockets/mud_telemetry.sock'
dnsmasq_msg = sys.argv
if len(dnsmasq_msg) == len(DNSMASQ_MSG_PARSE_ORDER):
    dnsmasq_info = dict(zip(DNSMASQ_MSG_PARSE_ORDER, dnsmasq_msg))
    if not dnsmasq_info['process'] == 'del':
        if ':' in dnsmasq_info['ip']:
            ip_version = 'ipv6'
        else:
            ip_version = 'ipv4'
        if dnsmasq_info['process'] == 'old':
            msg = json.dumps({"cmd": "add",
                              "details": {"mac_addr": dnsmasq_info['mac'], ip_version: dnsmasq_info['ip'],
                                          "name": dnsmasq_info['name']}}).encode('utf-8')
        elif check_eui64(dnsmasq_info['mac']):
            msg = json.dumps({"cmd": "old",
                              "details": {"mac_addr": dnsmasq_info['mac'], ip_version: dnsmasq_info['ip'],
                                          "name": dnsmasq_info['name']}}).encode('utf-8')
        else:
            msg = json.dumps({"cmd": "add",
                              "details": {"mac_addr": dnsmasq_info['mac'], ip_version: dnsmasq_info['ip'],
                                          "name": dnsmasq_info['name']}}).encode('utf-8')
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SERVER_ADDRESS)
        try:
            s.sendall(msg)
        finally:
            s.close()
