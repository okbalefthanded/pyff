# Lesson05 - Sending Markers
# Copyright (C) 2007-2009  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import socket

from FeedbackBase.Feedback import Feedback

class Lesson05(Feedback):
    
    def on_init(self):
        #self.send_parallel(0x1)
        self.logger.debug('Feedback on Init')
        self._udp_markers_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_udp("1")
        #print "Feedback initialized successfully."

    def on_play(self):
        self.logger.debug('Feedback on Play')
        #self.send_parallel(0x2)
        while True:
            self.send_udp("marker")
        #    print 'Feedback on play'

    def on_pause(self):
        self.logger.debug('Feedback on Pause')
        #self.send_parallel(0x4)
        self.send_udp("3")
        #print "feedback on pause"

    def on_stop(self):
        self.logger.debug('Feedback on stop')
        self.send_udp("stop")

    def on_quit(self):
        self.logger.debug('Feedback on quit')
        #self.send_parallel(0x8)
        self.send_udp("quit")
        print "feedback on quit"
