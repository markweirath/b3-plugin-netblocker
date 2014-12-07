# Netblocker plugin for B3

This plugin is an ip (range) blocker. Do not mistake this plugin with a firewall, because it does not provide that kind
of security. If you need to secure your system you should use a proper firewall.

This plugin can be used to prevent clients from playing on your B3 enabled server. It checks the IP address against
your list of blocked IP's when the client is authorized by B3. If the address is prohibited from connecting the client
will be kicked consequently.

Furthermore this plugin checks current active bans and tempbans and the corresponding IP addresses. It will also refuse 
those IP's aswell.

The plugin can handle only IPv4 type IP addresses and relies on the game/parser on providing that IP address to the plugin.

__This plugin only works with source code versions of the bot, not with the windows installer version due to library issues.__

## Ranges

The plugin can handle IP addresses or ranges in the following formats:

- single IP address: 127.0.0.1
- IP range: 127.0.0.1-127.0.0.100
- CIDR notation: 192.168.100.0/24
- combination of the above seperated by a comma (,)

### Example
    
    netblock: 127.0.0.1, 127.0.0.1-127.0.10.225, 168.0.0.0/8, 127.0/8

## Installation

1. copy the contents of the extplugins folder into your installations b3/extplugins folder.
2. add the plugin to your b3.xml config file:

        <plugin name="netblocker" config="@b3/extplugins/conf/netblocker.ini"/>

3. modify the netblocker.ini and add your unwanted IP's and ranges
4. restart the bot


----

_This plugin makes use of the netblock module for python created by 'siebenmann' (https://github.com/siebenmann/python-netblock)_