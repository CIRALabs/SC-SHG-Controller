import sqlite3
import sys
import time
import logging

logger = logging.getLogger('SC-SHG-Controller')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(stream_handler)
dnsmasq_info = sys.argv
logger.info('new msq from dnsmasq to {0} process: {1}, MAC address: {2}, IP address: {3}, and hostname: {4}'.format(
    *dnsmasq_info))
if not dnsmasq_info[1] == 'del':
    DB_PATH = "/srv/lxc/mud-supervisor/rootfs/app/fountain/production.sqlite3"
    LEASES_FILE_PARSE_ORDER = ['unix time', 'mac address', 'ip lease', 'host name', 'unknown']

    unix_time = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, eui64, ipv4 FROM devices")
    sqlite_info = cursor.fetchall()
    logger.debug('info from production db formatted(hostname,MAC address,IP address): {0}'.format(sqlite_info))
    if dnsmasq_info[2] not in [y[1] for y in sqlite_info]:
        cursor.execute(
            'INSERT INTO devices (name, eui64, ipv4, created_at, updated_at, quaranteed) VALUES (?, ?, ?, ?, ?, ?)',
            (dnsmasq_info[4], dnsmasq_info[2], dnsmasq_info[3], unix_time, unix_time, True))
        logger.info(
            'adding new device to production db hostname: {0}, MAC address: {1}, IP address: {2} unix_time: {3}'.format(
                dnsmasq_info[4], dnsmasq_info[2], dnsmasq_info[3], unix_time))
    elif not dnsmasq_info[4] == [y[2] for y in sqlite_info if y[1] == dnsmasq_info[2]][0]:
        cursor.execute('UPDATE devices SET ipv4 = ?, updated_at = ? WHERE eui64 = ?',
                       (dnsmasq_info[3], unix_time, dnsmasq_info[2]))
        logger.info(
            'updated device in production db MAC address: {0}, IP address: {1} unix_time: {2}'.format(dnsmasq_info[2],
                                                                                                      dnsmasq_info[3],
                                                                                                      unix_time))
    else:
        logger.info('device not updated MAC address: {0}'.format(dnsmasq_info[2]))
    conn.commit()
    conn.close()
