import socket
import sys
import re

DNSMASQ_MSG_PARSE_ORDER = ['sc-name', 'process', 'mac', 'ip', 'name']
SERVER_ADDRESS = 'socket4'
IPV4SEG = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'/.){3,3}' + IPV4SEG + r')'
dnsmasq_msg = sys.argv
if len(dnsmasq_msg) == len(DNSMASQ_MSG_PARSE_ORDER):
    dnsmasq_info = dict(zip(DNSMASQ_MSG_PARSE_ORDER, dnsmasq_msg))
    if not dnsmasq_info['process'] == 'del':
        if re.match(IPV4ADDR, dnsmasq_info['ip']) is None:
            ip_version = 'ipv6'
        else:
            ip_version = 'ipv4'
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SERVER_ADDRESS)
        try:
            s.sendall('{ "cmd" : "update", "details" : {"mac_addr" : "{0}", "{1}" : "{2}" ,"name" : "{3}" }}'.format(
                dnsmasq_info['mac'], ip_version, dnsmasq_info['ip'], dnsmasq_info['name']).encode('utf-8'))
        finally:
            s.close()
