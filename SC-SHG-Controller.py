import logging
import sqlite3
import sys
import time
import re

DNSMASQ_MSG_PARSE_ORDER = ['sc-name', 'process', 'mac', 'ip', 'name']
DB_PATH = "/srv/lxc/mud-supervisor/rootfs/app/fountain/production.sqlite3"
# DB_PATH = '/c/Users/daniel.innes/Documents/Repositories/SC-SHG-Controller/testing/testing.sqlite3'
IPV4SEG = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'/.){3,3}' + IPV4SEG + r')'


def process_dnsmasq_info():
    if not dnsmasq_info['process'] == 'del':
        ip_version = 'ipv6' if re.match(IPV4ADDR, dnsmasq_info['ip']) is None else 'ipv4'
        unix_time = int(time.time())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, eui64, {0} FROM devices".format(ip_version))
        sqlite_info = cursor.fetchall()

        logger.debug('info from production db formatted(hostname,MAC address,IP address): %s', sqlite_info)
        if dnsmasq_info['mac'] not in [y[1] for y in sqlite_info]:
            cursor.execute(
                'INSERT INTO devices (name, eui64, {0}, created_at, updated_at, quaranteed) VALUES (?, ?, ?, ?, ?, ?)'.format(
                    ip_version),
                (dnsmasq_info['name'], dnsmasq_info['mac'], dnsmasq_info['ip'], unix_time, unix_time, True))
            logger.info(
                'adding new device to production db hostname: %s, MAC address: %s, IP address: %s unix_time: %s',
                dnsmasq_info['name'], dnsmasq_info['mac'], dnsmasq_info['ip'], unix_time)
        elif not dnsmasq_info['ip'] == [y[2] for y in sqlite_info if y[1] == dnsmasq_info['mac']][0]:
            cursor.execute('UPDATE devices SET {0} = ?, updated_at = ? WHERE eui64 = ?'.format(ip_version),
                           (dnsmasq_info['ip'], unix_time, dnsmasq_info['mac']))
            logger.info(
                'updated device in production db MAC address: %s, IP address: %s unix_time: %s',
                dnsmasq_info['mac'], dnsmasq_info['ip'], unix_time)
        else:
            logger.info('device not updated MAC address: %s', dnsmasq_info['mac'])
        conn.commit()
        conn.close()


if __name__ == '__main__':
    logger = logging.getLogger('SC-SHG-Controller')
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(stream_handler)

    dnsmasq_msg = sys.argv

    try:
        if len(dnsmasq_msg) == len(DNSMASQ_MSG_PARSE_ORDER):
            dnsmasq_info = dict(zip(DNSMASQ_MSG_PARSE_ORDER, dnsmasq_msg))
            logger.info('new msg from dnsmasq to %s process: %s, MAC address: %s, IP address: %s, and hostname: %s',
                        dnsmasq_info['sc-name'], dnsmasq_info['process'], dnsmasq_info['mac'], dnsmasq_info['ip'],
                        dnsmasq_info['name'])
            process_dnsmasq_info()
        else:
            logger.error('unable to parse msg from dnsmasq, dnsmasq_msg: %s', dnsmasq_msg)
    except sqlite3.OperationalError:
        logger.exception('unable to open database file at %s', DB_PATH)
    except Exception as error:
        logger.exception('unexpected error processing msg from dnsmasq, dnsmasq_msg: %s', dnsmasq_msg)
