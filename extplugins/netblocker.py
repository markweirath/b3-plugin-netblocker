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
import b3.extplugins.netblock as netblock

# --------------------------------------------------------------------------------------------------
class NetblockerPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    _blocks = []
    # FrostBite Games depend on PB event to gather IP
    _frostBiteGameNames = ['bfbc2', 'moh', 'bf3', 'bf4']

    def __init__(self, console, config=None):
        """
        Object constructor.
        :param console: The console instance
        :param config: The plugin configuration
        """
        self._adminPlugin = None          # admin plugin object reference
        self.query = None                 # shortcut to the storage.query function
        b3.plugin.Plugin.__init__(self, console, config)

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

        # define a shortcut to the storage.query function
        self.query = self.console.storage.query

        if self.console.gameName in self._frostBiteGameNames:
            self.registerEvent(b3.events.EVT_PUNKBUSTER_NEW_CONNECTION)
        else:
            self.registerEvent(b3.events.EVT_CLIENT_AUTH)

        self.debug('Banned Ips:')
        self.getBanIps()
        self.debug('Banned Ips:')
        self.getTempBanIps()


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
            self._maxLevel = self.config.get('settings', 'maxlevel')
        except Exception, err:
            self.error(err)
        self.debug('Maximum level affected: %s' % self._maxLevel)
        try:
            self._blockBans = self.config.getboolean('settings', 'blockbans')
        except Exception, err:
            self.error(err)
        self.debug('Block bans: %s' % self._blockBans)

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

        # check the level of the connecting client before applying the filters
        if client.maxLevel > self._maxLevel:
            self.debug('%s is a higher level user, and allowed to connect' % client.name)
            return True
        # check for active bans and tempbans
        elif self._blockBans and client.ip in self.getBanIps():
            self.debug('Client refused: %s - %s' % (client.name, client.ip))
            message = 'Netblocker: Client refused: %s (%s) has an active Ban' % (client.ip, client.name)
            client.kick(message)
            return False
        elif self._blockBans and client.ip in self.getTempBanIps():
            self.debug('Client refused: %s - %s' % (client.name, client.ip))
            message = 'Netblocker: Client refused: %s (%s) has an active TempBan' % (client.ip, client.name)
            client.kick(message)
            return False
        # apply the refused netblocks
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
                    self.debug('Client refused: %s (%s)' % (client.ip, client.name))
                    message = "Netblocker: Client %s refused!" % client.name
                    client.kick(message)
                    return False

    def getBanIps(self):
        q = """SELECT penalties.id, penalties.type, penalties.time_add, penalties.time_expire, penalties.reason, penalties.inactive, penalties.duration, penalties.admin_id, target.id as target_id, target.name as target_name, target.ip as target_ip, target.guid FROM penalties, clients as target WHERE penalties.type = 'Ban' AND inactive = 0 AND penalties.client_id = target.id AND ( penalties.time_expire = -1) ORDER BY penalties.id DESC"""
        cursor = self.query(q)
        if not cursor:
            return []
        _penalties = []
        while not cursor.EOF:
            _penalties.append(cursor.getRow())
            cursor.moveNext()
        cursor.close()

        _bannedIps = []
        for _p in _penalties:
            _bannedIps.append(_p['target_ip'])
        self.debug(_bannedIps)

    def getTempBanIps(self):
        q = """SELECT penalties.id, penalties.type, penalties.time_add, penalties.time_expire, penalties.reason, penalties.inactive, penalties.duration, penalties.admin_id, target.id AS target_id, target.name AS target_name, target.ip AS target_ip, target.guid FROM penalties INNER JOIN clients target ON penalties.client_id = target.id WHERE penalties.type = 'TempBan' AND penalties.inactive = 0 AND penalties.time_expire >= UNIX_TIMESTAMP(NOW()) + 432000 ORDER BY  penalties.id DESC"""
        cursor = self.query(q)
        if not cursor:
            return []
        _penalties = []
        while not cursor.EOF:
            _penalties.append(cursor.getRow())
            cursor.moveNext()
        cursor.close()

        _bannedIps = []
        for _p in _penalties:
            _bannedIps.append(_p['target_ip'])
        self.debug(_bannedIps)

if __name__ == '__main__':
    print '\nThis is version ' + __version__ + ' by ' + __author__ + ' for BigBrotherBot.\n'
