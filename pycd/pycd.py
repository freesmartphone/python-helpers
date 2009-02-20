#!/usr/bin/env python
"""
The Open Device Daemon - Python Implementation

(C) 2008 Michael 'Mickey' Lauer <mlauer@vanille-media.de>
(C) 2008 Openmoko, Inc.
GPLv2 or later
"""

import os, sys

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import runpy

import logging
# create logger
logger = logging.getLogger( "pycd" )
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter( "%(asctime)s - %(name)s - %(levelname)s - %(message)s" )
handler.setFormatter( formatter )
logger.addHandler( handler )

#============================================================================#
class Prototype( object ):
#============================================================================#
    def __init__( self ):
        logger.info( "starting prototype" )
        self.down = os.pipe()
        self.up = os.pipe()
        pid = os.fork()
        if pid:
            self.inParent( pid )
        else:
            self.inChild()
            os._exit(0)

    def inChild( self ):
        logger.info( "in prototype" )
        sys.argv[0] = "pycd - prototype"
        os.close( self.down[1] )
        os.close( self.up[0] )
        self.down = os.fdopen( self.down[0], 'r', 0 ) # read side
        self.up = os.fdopen( self.up[1], 'w', 0 ) # write side
        while True:
            sender, argv = self.down.readline().strip().split(' ', 1)
            sender = int( sender )
            argv = eval( argv )
            logger.info( "got command: %s", repr(( sender, argv )) )
            self.doClone( sender, argv )

    def inParent( self, child_pid ):
        logger.info( "started prototype (child PID %s)", child_pid )
        os.close( self.down[0] )
        os.close( self.up[1] )
        self.down = os.fdopen( self.down[1], 'w', 0) # write side
        self.up = os.fdopen( self.up[0], 'r', 0) # read side

    def requestClone( self, sender, argv ):
        self.down.write( "%i %s\n" % ( sender, repr( argv ) ) )
        reply = int( self.up.readline().strip() )
        logger.info( "got reply: %s", repr(reply) )
        return int( reply )

    def doClone( self, sender, argv ):
        pid = os.fork()
        if pid:
            os.waitpid( pid, 0 )
            return

        os.chdir( "/proc/%i/cwd" % sender )
        os.setsid()
        os.umask(0)

        for line in file( "/proc/%i/status" % sender, 'r' ):
            line = line.strip().lower().split()
            if line[0] == "uid:":
                uid = int( line[1] )
            elif line[0] == "gid:":
                gid = int( line[1] )
            elif line[0] == "groups:":
                groups = map( int , line[1:])

        environ = file( "/proc/%i/environ" % sender, 'r' ).read()
        for key in os.environ.keys():
            del os.environ[key]
        for line in environ.split( '\x00'):
            if not line:
                continue
            key, value = line.split( '=', 1 )
            os.environ[key] = value

        os.setgid( gid )
        os.setgroups( groups )
        os.setuid( uid )

        pid = os.fork()
        if pid:
            os._exit(0)

        logger.info( "in child" )
        self.down.close()
        MAXFD = os.sysconf( 'SC_OPEN_MAX' )
        for fd in xrange( 3, MAXFD ):
            if fd == self.up.fileno():
                continue # will be closed later
            try:
                os.close( fd )
            except OSError:
                pass
        sys.stdout.flush()
        sys.stderr.flush()
        stdin = file( "/proc/%i/fd/0" % sender, 'r')
        stdout = file( "/proc/%i/fd/1" % sender, 'a+')
        stderr = file( "/proc/%i/fd/2" % sender, 'a+', 0)
        os.dup2( stdin.fileno(), sys.stdin.fileno() )
        os.dup2( stdout.fileno(), sys.stdout.fileno() )
        os.dup2( stderr.fileno(), sys.stderr.fileno() )

        self.up.write( "%s\n" % os.getpid() )
        self.up.close()
        self.runClone( argv )
        sys.exit(0)

    def runClone( self, argv ):
        sys.argv = argv
        runpy.run_module(sys.argv[0], run_name="__main__", alter_sys=True)

#============================================================================#
class CloneFactory( dbus.service.Object ):
#============================================================================#
    DBUS_PATH = "/"
    DBUS_INTERFACE = "org.freesmartphone.CloneFactory"
    def __init__( self, bus ):
        dbus.service.Object.__init__( self, bus, self.DBUS_PATH )
        self.bus = bus
        self.dbus_proxy = self.bus.get_object( "org.freedesktop.DBus", "/" )
        self.dbus_iface = dbus.Interface( self.dbus_proxy, "org.freedesktop.DBus" )

    @dbus.service.method( DBUS_INTERFACE, 'a(s)', 'i', sender_keyword='sender' )
    def AdoptClone( self, argv, sender ):
        logger.info( "AdoptClone" )
        sender_pid = int( self.dbus_iface.GetConnectionUnixProcessID( sender ) )
        logger.info( "Sender: %s", repr( sender) )
        logger.info( "PID: %s", repr( sender_pid ) )
        argv = map( str, argv )
        return prototype.requestClone( sender_pid, argv )

#=========================================================================#
class Controller( object ):
#=========================================================================#
    def __init__( self ):
        logger.info( "starting controller" )
        DBusGMainLoop( set_as_default=True )
        self.mainloop = gobject.MainLoop()
        gobject.idle_add( self.idle )
        gobject.timeout_add_seconds( 10, self.timeout )
        self.bus = dbus.SystemBus()
        self.busname = dbus.service.BusName( "org.freesmartphone.CloneFactory", self.bus )
        self.objects = []
        self.objects.append( CloneFactory( self.bus ) )

    def idle( self ):
        logger.info( "in mainloop" )
        return False

    def timeout( self ):
        logger.info( "alive and kicking" )
        return True

    def run( self ):
        self.mainloop.run()

if __name__ == "__main__":
    prototype = Prototype()
    controller = Controller()
    controller.run()

