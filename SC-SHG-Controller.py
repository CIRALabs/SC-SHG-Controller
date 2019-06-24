import sqlite3
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

DB_PATH = "/srv/lxc/mud-supervisor/rootfs/app/fountain/production.sqlite3"
LEASES_FILE = "/var/dhcp.leases"
LEASES_FILE_PARSE_ORDER = ['unix time', 'mac address', 'ip lease', 'host name', 'unknown']


def on_modified(_):
    unix_time = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, eui64, ipv4 FROM devices")
    sqlite_info = cursor.fetchall()
    with open(LEASES_FILE, 'r') as leases_file:
        leases = {lease['host name']: {key: lease[key] for key in ['unix time', 'ip lease', 'mac address']}
                  for lease in
                  map(lambda lease: dict(zip(LEASES_FILE_PARSE_ORDER, lease.split(' '))), leases_file.readlines())}
    dnsmasq_info = [[key, lease['mac address'], lease['ip lease']] for key, lease in leases.items()]
    devices_to_add = []
    devices_to_edit = []
    print(sqlite_info, dnsmasq_info)
    for info in dnsmasq_info:
        if info[1] not in [y[1] for y in sqlite_info]:
            devices_to_add.append((info[0], info[1], info[2], unix_time, unix_time, True))
        elif not info[2] == sqlite_info[info[1]][2]:
            devices_to_edit.append((info[2], unix_time, info[0]))
    print(devices_to_add, devices_to_edit)
    cursor.executemany(
        'INSERT INTO devices (name, eui64, ipv4, created_at, updated_at, quaranteed) VALUES (?, ?, ?, ?, ?, ?)',
        devices_to_add)
    cursor.executemany(
        'UPDATE devices SET ipv4 = ?, updated_at = ? WHERE eui64 = ?',
        devices_to_edit)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    event_handler = PatternMatchingEventHandler(patterns=['*/' + LEASES_FILE.split('/')[-1]])
    event_handler.on_modified = on_modified
    observer = Observer()
    observer.schedule(event_handler, '/'.join(LEASES_FILE.split('/')[:-1]))
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
