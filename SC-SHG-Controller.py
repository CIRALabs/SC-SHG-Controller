import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sqlite3

DB_PATH = "/srv/lxc/mud-supervisor/rootfs/app/fountain/production.sqlite3"
LEASES_FILE = "/var/dhcp.leases"
LEASES_FILE_PARSE_ORDER = ['unix time', 'mac address', 'ip lease', 'host name', 'unknown']


def on_modified(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, eui64 FROM devices")
    sqlite_info = cursor.fetchall()
    with open(LEASES_FILE, 'r') as leases_file:
        leases = {lease['host name']: {key: lease[key] for key in ['unix time', 'ip lease', 'mac address']}
                  for lease in
                  map(lambda lease: dict(zip(LEASES_FILE_PARSE_ORDER, lease.split(' '))), leases_file.readlines())}
    dnsmasq_info = [[key, lease['mac address']] for key, lease in leases.items()]
    devices_to_add = []
    print(sqlite_info, dnsmasq_info)
    for info in [x for x in dnsmasq_info if x[1] not in [y[1] for y in sqlite_info]]:
        unix_time = int(time.time())
        devices_to_add.append((info[0], info[1], unix_time, unix_time, True))
    print(devices_to_add)
    cursor.executemany('INSERT INTO devices (name, eui64, created_at, updated_at, quaranteed) VALUES (?, ?, ?, ?, ?)',
                       devices_to_add)
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
