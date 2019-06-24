import sqlite3
import sys
import time

dnsmasq_info = sys.argv  # [someting,process,mac,ip,name]
print(dnsmasq_info)
if not dnsmasq_info[1] == 'del':
    DB_PATH = "/srv/lxc/mud-supervisor/rootfs/app/fountain/production.sqlite3"
    LEASES_FILE = "/var/dhcp.leases"
    LEASES_FILE_PARSE_ORDER = ['unix time', 'mac address', 'ip lease', 'host name', 'unknown']

    unix_time = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, eui64, ipv4 FROM devices")
    sqlite_info = cursor.fetchall()
    devices_to_add = []
    devices_to_edit = []
    print(sqlite_info, dnsmasq_info)
    if dnsmasq_info[2] not in [y[1] for y in sqlite_info]:
        devices_to_add.append((dnsmasq_info[4], dnsmasq_info[2], dnsmasq_info[3], unix_time, unix_time, True))
    elif not dnsmasq_info[4] == [y[2] for y in sqlite_info if y[1] == dnsmasq_info[2]][0]:
        devices_to_edit.append((dnsmasq_info[3], unix_time, dnsmasq_info[2]))
    print(devices_to_add, devices_to_edit)
    cursor.executemany(
        'INSERT INTO devices (name, eui64, ipv4, created_at, updated_at, quaranteed) VALUES (?, ?, ?, ?, ?, ?)',
        devices_to_add)
    cursor.executemany(
        'UPDATE devices SET ipv4 = ?, updated_at = ? WHERE eui64 = ?',
        devices_to_edit)
    conn.commit()
    conn.close()
