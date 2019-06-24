# SC-SHG-Controller
CIRA Labs Project information: https://cira.ca/cira-secure-home-gateway
The process SC-SHG Controller learns of the new association and collects the connection information on the device.
The device may be new, or may just be reconnecting; both events are interesting.
Devices are indexed by their layer-2 address (ethernet mac address).
The process then communicates with the mud-supervisor and updates it’s list of devices and the status of the device. 
The SC ensures the MUD controller DB is in sync with connected devices (WIFI and LAN based).