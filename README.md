# SC-SHG-Controller
## CIRA Labs Project information: [SHG](https://cira.ca/cira-secure-home-gateway)
The process SC-SHG-Controller learns of the new association and collects the connection information on the device.
The device may be new, or may just be reconnecting; both events are interesting.
Devices are indexed by their layer-2 address (ethernet mac address).
The process then communicates with the mud-supervisor and updates it’s list of devices and the status of the device. 
The SC ensures the MUD controller DB is in sync with connected devices (WIFI and LAN based).
## Test Notes
1. Copy SC-SHG-Controller.py and dhcp-script.sh to the SHG
2. Edit [/etc/config/dhcp](https://openwrt.org/docs/guide-user/base-system/dhcp) to add ```option dhcpscript 'PATH_TO_dhcp-script.sh'``` to ```config dnsmasq```
3. Edit dhcp-script.sh to contain the path to SC-SHG-Controller.py e.g. ```python3 /media/usb/SC-SHG-Controller.py $1 $2 $3 $4```
4. restart dnsmasq ```service dnsmasq restart```
5. output logs are in [/var/log/messages](https://openwrt.org/docs/guide-user/base-system/log.essentials)
