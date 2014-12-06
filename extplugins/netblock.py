#
# Netblocker Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2014 Mark Weirath (xlr8or@xlr8or.com)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA    02110-1301    USA
#
# netblocker module provided by siebenmann: https://github.com/siebenmann/python-netblock

# Changelog:
# 06-12-2014 : v1.0.0beta : xlr8or
# * First edition of the netblocker

__version__ = '1.0.0beta'
__author__ = 'xlr8or'

import b3
import b3.events
import b3.plugin
import netblock

# --------------------------------------------------------------------------------------------------
class NetblockPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    _blocks = []
    # FrostBite Games depend on PB event to gather IP
    _frostBiteGameNames = ['bfbc2', 'moh', 'bf3', 'bf4']


    def startup(self):
        """\
        Initialize plugin settings
        """

        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False

        if self.console.gameName in self._frostBiteGameNames:
            self.registerEvent(b3.events.EVT_PUNKBUSTER_NEW_CONNECTION)
        else:
            self.registerEvent(b3.events.EVT_CLIENT_AUTH)

        self.debug('Started')

    def onLoadConfig(self):
        try:
            # seperate entries on the ,
            _l = self.config.get('settings', 'netblock').split(',')
            # strip leading and trailing whitespaces from each list entry
            self._blocks = [x.strip() for x in _l]
        except Exception, err:
            self.error(err)
        self.debug('Refused netblocks: %s' % self._blocks)
        try:
            self._maxLevel = self.config.getint('settings', 'maxlevel')
        except Exception, err:
            self.error(err)
        self.debug('Maximum level affected: %s' % self._maxLevel)


    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        # EVT_CLIENT_AUTH is for q3a based games, EVT_PUNKBUSTER_NEW_CONNECTION is a PB related event for BF:BC2
        if event.type == b3.events.EVT_CLIENT_AUTH or event.type == b3.events.EVT_PUNKBUSTER_NEW_CONNECTION:
            self.onPlayerConnect(event.client)

    def onPlayerConnect(self, client):
        """\
        Examine players ip address and allow/deny connection.
        """
        self.debug(
            'Checking player: %s, name: %s, ip: %s, level: %s' % (client.cid, client.name, client.ip, client.maxLevel))

        if client.maxLevel > self._maxLevel:
            self.debug('%s is a higher level user, and allowed to connect' % client.name)
            return True
        else:
            # transform ip address
            _ip = netblock.convert(client.ip)
            # cycle through our blocks
            for _block in self._blocks:
                # convert each block
                _b = netblock.convert(_block)
                # check if clients ip is in the disallowed range
                if _b[0] <= _ip[0] <= _b[1]:
                    # client not allowed to connect
                    self.debug('Client refused: %s - %s' % (client.name, client.ip))
                    message = "Netblocker: Client %s refused!" % client.name
                    self.console.say(message)
                    client.kick(silent=True)
                    return False

if __name__ == '__main__':
    print '\nThis is version ' + __version__ + ' by ' + __author__ + ' for BigBrotherBot.\n'
