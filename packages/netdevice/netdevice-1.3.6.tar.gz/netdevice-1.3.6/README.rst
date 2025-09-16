netdevice
*********

Python modules to execute command on remote network device.

To install easily::

    pip install -U netdevice

1. Introduction
===============

netdevice is a python module that allow you run shell command on local or
remote host in python. It's especially useful for network test automation:

When host is given, you can run the command on remote host and get the result
in the return:

.. code-block:: python

    from netdevice import cisco, junos, linux
    pc = linux.LinuxDevice("ssh://dev:1234@10.208.72.12")
    print(pc.cmd("ifconfig eth1"))

When the "server" parameter is not given, it run on local device and get the
result:

.. code-block:: python

    from netdevice import cisco, junos, linux
    #It ack as pc = linux.LinuxDevice("ssh:127.0.0.1")
    pc = linux.LinuxDevice()
    print(pc.cmd("whoami"))

Use help command show the documents::

    from netdevice import cisco, junos, linux
    help(linux)
    help(junos)
    help(cisco)

2. Feature
==========

    1) Python Based: Plenty of features
    2) Environmentally friendly: can run anywhere where there is python and connect to the devices.
    3) Easy to Learn: Need know little about Python
    4) Easy to write: One case only have several to dozens of lines.
    5) Faster: run the testbed from local and is much faster.
    6) object oriented: Flexible and Easy to extend

3. Test architecture based on netdevice
===========================================

::

    +---------------------------------+------------+----------------------+
    |                                 |            | case1                |
    |                                 |            +----------------------+
    |  One case                       | Test Suite | ...                  |
    |                                 |            +----------------------+
    |                                 |            | caseN                |
    +---------------------------------+------------+----------------------+
    |  netdevice                                                          |
    |                                                                     |
    |  PC1                  DUT                  DUT                      |
    |  +---------------+    +---------------+    +---------------+        |
    |  | Linux devices |    | Junos devices |    | Cisco devices |  ...   |
    |  +---------------+    +---------------+    +---------------+        |
    |                       | Linux devices |    | Linux devices |  ...   |
    |                       +---------------+    +---------------+        |
    +---------------------------------------------------------------------+

                     Test Architecture based on netdevice
 
4. Object overview
==================

4.1 LinuxDevice
---------------

4.1.1 Constructor
+++++++++++++++++

LinuxDevice is a common abstraction for linux like devices. It' flexible to
define a LinuxDevice object by two main means.

1) Use a url to define a netdevice, then you can execute the command and get
the result:

By desginating the necessary attribute such as expect/preconfig/postconfig, you
can run it on devices with special prompt, run the given commands when login
succeed, etc.

.. code-block:: python

    client = linux.LinuxDevice("ssh://root:1234@englab.ent-vm02.test.net",
            expect = ["FW1#", "FW1\(config\)#", "FW1\[DBG\]#"],
            preconfig = ["configure", "console timeout 0", "end", "terminal length 0"])
    server = linux.LinuxDevice("telnet://root:1122@10.208.172.45:7012")
    print(client.cmd("ifconfig").msg)
    print(server.cmd("pwd").msg)

note::

    The "[()]" characters in the expect string should be escaped as '\[\(\)\]'.

2) Use the dictionary to describe the device, it's very useful for test
script. 

If you test device has special prompt, you must list all of them in the expect
parameters.

for examples:

.. code-block:: python

    skater = {"url": "telnet://root:1234@skater.englab.test.net:2006",
            "eth0": {"name": "reth0.0", "ip": "192.168.1.1/24", "ip6": "2002::11/64","zone": "trust" },
            "eth1": {"name": "reth1.0", "ip": "192.168.2.1/24", "ip6": "2001::11/64","zone": "untrust" },
            expect: ["FW1#", "FW1\(config\)#", "FW1\[DBG\]#"],
            preconfig: ["configure", "console timeout 0", "end", "terminal length 0"],
            }
    vm01 = {"url": "ssh://root:1234@ent-vm02.englab.test.net",
            "eth0": {"name": "eth1", "ip": "192.168.1.2/24", "route": "192.168.2.0/24", "gateway": "192.168.1.1"},
            "expect": ["FW1#", "FW1\(config\)#", "FW1\[DBG\]#"],
            }
    vm02 = {"url": "ssh://root:1234@ent-vm02.englab.test.net",
            "eth0": {"name": "eth1", "ip": "192.168.2.2/24", "route": "192.168.1.0/24", "gateway": "192.168.2.1"},
            }
    pc1 = linux.LinuxDevice(**vm01)
    pc2 = linux.LinuxDevice(**vm02)
    dut = junos.JunosDevice(**skater)
    print(pc1.cmd("ifconfig"))
    print(pc1["eth0"]["ip"])
    dut.cli("show security flow status")

4.1.2 Attributes
++++++++++++++++

LinuxDevice operate based on its attributes. User input those attributes and
can use them after that. Some attributes are pre-defined and the LinuxDevices
will use them when login, log, configuration and so on. use can change those
attribtes. Other attrubutes are defined totally by users and user define how
to use them.

1) Pre-defined attributes:

I list the following pre-define attributes and their default value and the
meaning of them.

.. code-block:: python

    default = {
        # mandtory, if not given, it will fail to construct a device
        "scheme":     "ssh",     # login method, default is ssh, support ssh
                                 # and telnet now;
        "username":      None,   # Usename to login;
        "hostname":          None,   # A ip address or hostname that can connect
         
        # Optional, if not given, use the default
        "password":      None,   # Password to login, could be omitted if use
                                 # public key;
        "root_password": None,   # Root password is used since some configuration
                                 # need root privillage. If not provided, some
                                 # configurationa or command would fail since
                                 # privilage.
        "url":       None,       # url to connect the server, use url insteading
                                 # scheme/username/passowrd/hostname/port
        "name":       None,      # name of the devices, only used for log. if not
                                 # set, the first part of hostname is used.
        "autologin":  True,      # If ture, will login the devices immediately.
        "expect":  [],           # The expected prompt list.
        "preconfig":  [],        # A list of cmd/configuration the device will
                                 # configure before test;
        "postconfig": [],        # A list of cmd/configuration the device will
                                 # configure after test;
                                  
        # log related
        "log_file": "test_%s.log" %(time.strftime("%Y%m%d%H%M%S", time.localtime())),
                                 # log files, set None to disable recording log in file.
        "log_level":  LOG_INFO,  # log level, 0-7, the higher it's, the more log
                                 # recorded.
        "log_color":  None,      # log color, if not set will choose randomly;
                                 # Use self.test_color() to see what each color
                                 # looks like
        "log_time":   True,      # record the log with local time;
        #"log_thread": True,      # record the log with thread name;

        # User can also define Whatever attributes you want.
        # ...
    }

2) User-defined attributes:

Besides the pre-defined attributes, user can define their own attributes,
since those kinds of attributes are used for user only, they can be in any
type, for examples:

.. code-block:: python

    client = linux.LinuxDevice("telnet://root:1122@10.208.172.45:7012",
                               "int0": { 'name': 'eth1', 'inet': '42.0.0.2/24', 'inet6': '2002::2/64'},
                               description = "Beijing")
    client["season"] = "summer"
    print(client["season"], client["description"])
    print(client["int0"]["inet"])

4.1.3 Methods
+++++++++++++

LinuxDevice support the folowing method:

netdevice.linux.LinuxDevice.__init__(self, server=None, \*\*kwargs):
    This is the constructor for LinuxDevice, The parameter pass the attribute
    that the object needs.

    @server: the standard url of the server, support the query parameters.

    @kwargs: attributes of the server, the parameter in this part could be
    used as the attribute of the object.

    Example::

        client = linux.LinuxDevice("telnet://root:1122@10.208.172.45:7012",
                                   "eth0": {"name": "eth1",
                                   "ip": "192.168.1.2/24",
                                   "route": "192.168.2.0/24",
                                   "gateway": "192.168.1.1"},
                                   description = "Beijing")

netdevice.linux.LinuxDevice.__del__(self):
    Recycle resource when the object is destroied.

netdevice.linux.LinuxDevice.login(self, terminal_type='ansi', login_timeout=10):
    Connect the object with the constructor attribute.

    The defualt attribute “autologin” is True, so normally it will be auto called. Set attribute “autologin” as False and you must call it explictly.

netdevice.linux.LinuxDevice.relogin(self):
    Kill the current session and relogin.

netdevice.linux.LinuxDevice.cmd(self, \*args, \*\*kwargs):
    Execute a command and return the result of the last command. the result
    include the output(msg) and return code(rc):

    @msg: the output in the screen.

    @rc: return code, <0 means failure or timeout, 0 means match the 1st expected value, 1 means match the 2nd expected value, etc…

    For examples::

        (output, rc) = pc1.cmd("ls", format = "both")
        pc1.assert_value(rc >= 0, "")
        self.log(output)

netdevice.linux.LinuxDevice.__cmd(self, cmd, expect=None, timeout=20, background=False, logfile='/dev/null', control=False, format='output', log_command_leading='\x1b[0;31m$ \x1b[0m', log_command_color='no_color', log_command_bg_color='no_color', log_output_color='no_color', log_output_bg_color='no_color', \*\*kwargs):
    Execute a command provided by @cmd on remote Linuxdevice and return the
    execution result, If the @expect is found, it succeed and return
    immediately, or it will wait for at most @timeout seconds. The return
    result will be desginated by @format:

    @ expect: the prompt the execute is expected to include. If not
    provided, the self.prompt is used. For some applications, i.e ftp, it will
    not use the system’s prompt so you must give the expected prompt.

    @ timeout: Hong long to wait before it’s thinked as timeout, if it
    timeout a “CTRL + C” will be trriggered, so please set the proper timeout
    carefully;

    @ background: Go to background immediately after startup. If no output
    file is specified via the -o, output is redirected to /dev/null.

    @ logfile: Log all messages to logfile on the remote linux device. The
    messages are normally reported to standard error.

    @ control: If it is True, send a control character to the child such as
    Ctrl-C or Ctrl-D. For example, to send a Ctrl-G (ASCII 7)::

        self.cmd('g', control = True)

    @ format: "output", it return the screen output.
    "status", it return the execute status. i(>0) means it execute
    successfully and match the i-th expected prompt.
    "both", it return both of the above.

    @ log_command_leading: Which leading chars to add before command in the log.

    @ log_command_color: Which color to show the command in the log.

    @ log_command_bg_color: Which background color to show the command in the log.

    @ log_output_color: Which color to show the output in the log.

    @ log_output_bg_color: Which background color to show the output in the log.

    @ redirect: Noramlly the output would be shown on screen or log file,

    if this is set then the output of the command would be saved in the given
    file, it’s especially useful for execute command with big output. redirect
    = “/dev/null” would redirect the output to a hole. For example::

        pc.cmd("ifconfig", redirect = "ifconfig_result.log")

    [CAUTION]: please increase the timeout value if the command is time-consuming, or it will cause failure.

netdevice.linux.LinuxDevice.log(self, message, level=5, leading=None, color='no_color', bg_color='no_color', log_level=None, \*\*kwargs):
    record the log to file self[“log_file”] with the color self[“log_color”
    ], with the local time if self[‘log_time’] is True, the log looks like::

        [2017-05-16 16:02:07][ regazara ]: ssh login succeed.

    @ message: The log text.

    @ level: The log level of the text. Will not show if it’s large than the self[“log_level”].

    @log_level: will override the level

    @ color: The log color of the text.

    @ bg_color: The log background color of the text.

netdevice.linux.LinuxDevice.sleep(self, timeout, total=50, char='>', description='sleep'):
    Sleep with progress bar, the granularity is 0.1 second. something like
    that::

        sleep 7/10[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ][71%]

netdevice.linux.LinuxDevice.get_file(self, filename, localname='.', scheme='scp', timeout=-1):
    Get file from current host by scp.

    @filename: file to get from the host.

    @localname: save name after download

    @timeout: How long to wait for the files to be downloaded. Default is neveer timeout

netdevice.linux.LinuxDevice.get_files(self, \*args, \*\*kwargs):
    Get files from current host by scp.

netdevice.linux.LinuxDevice.put_file(self, filename, remotedir, timeout=-1):
    put file to current host by scp.

    @filename: file to put from the local. local means the host where you
    execute this scriopt.

    @remotedir: save name after upload.

    @timeout: How long to wait for the files to be uploaded. If the file is
    very big, set it to a big value or it will fail.

4.2 JunosDevice
---------------

4.2.1 Constructor
+++++++++++++++++

JunosDevice is a common abstraction for test network devices. It derives
from LinuxDevice so it has every method of LinuxDevice, except some of them
are overrided. Please use the similar way to define a JunosDevice, for
example:

.. code-block:: python

    dut = junos.JunosDevice("ssh://root:test@10.219.29.61")
    print(dut["username"])
    print(dut.cli("show security flow session"))

4.2.2 Methods
+++++++++++++

Besides all the methods derived from LinuxDevice, JunosDevice support the
folowing extra methods:

    def cmd (self, cmd, mode = "shell", timeout = 30, \*\*kwargs):

        There are total 4 modes for junos devices:

            1) shell: execute the command in shell mode and return the result,
                this is the default mode and it looks like linux.cmd().

            2) cli: execute the command in cli mode and return the result,
                self.cmd(cmd, mode = "cli") equal to self.cli(cmd), see detail
                in seld.cli()

            3) configure: execute the command in configure mode and return the
                result, self.cmd(cmd, mode = "configure") equal to
                self.configure(cmd), see detail in seld.configure()

            4) vty: execute the command in vty mode and return the result,
                self.cmd(cmd, mode = "vty") equal to self.vty(cmd), see detail
                in seld.vty()

        Supported options include:

            timeout: time to wait for the execute command return. default is 5
                     seconds

    cli (self, cmd, parse = None, timeout = 30, \*\*kwargs):

        equal cmd(..., mode = "cli")

        Execute a list of cli command and return the execution result of the
        last command.

        @parse: Normally, the result will be plain text or xml text. But if
        the @parse is given, the result will be parsed and a list of
        dictionary for @parse will be returned. It's useful to parse the xml
        result. For example the following command return a list of session in
        dictionary::
        
            sessions = dut.cli('show security flow session',
                               parse = "flow-session")
            print sessions[0]['session-identifier']

        while the following command will return the plain text result::

            output = dut.cli('show security flow session')
            print output

    configure(self, cmd, \*\*kwargs):

        equal cmd(..., mode = "configure"), Execute a configure command and
        return the result of the last command. Sematics is like self.cli, see
        detail in self.cli(), For example, Execute a configure command::

            dut.configure('set security flow traceoptions flag all')
            dut.configure('set security traceoptions file flow.log size 50m')
            dut.configure('set security traceoptions level verbose')
            dut.configure('set security traceoptions flag all')
            dut.configure('commit')

    def vty (self, \*args, \*\*kwargs):

        equal cmd(..., mode = "vty")

        Execute every line in every argument on every SPU(if not given) and
        return the result.

        Supported options include:

            timeout: time to wait for the execute command return. default is 5
                     seconds
            tnp_addr: tnp address to execute, if not execut the command on
                      every SPU.

    def get_spus (self, \*\*kwargs):
    
        Get the spu list of the srx.

    print_session (self, session):
        
        Convert a or lists of session in dictionary to plain text. print it as
        show of "show security flow session".

        @session: it could be a session or a list of session.

    install_image (self, image):
        
        Install a image and reboot the dut, wait until it is up with all
        SPU/SPC.
        
        @local: install a local image, first upload the image to /var/tmp/ on
        the DUT and then install it.

        @remote: install a image on the DUT

4.3 Define your own device
----------------------------

The core concept for netdevice and pexpect is the prompt. If you know the promt
in your device, you can define your own device by giving "expect" parameter.

For example, your device's prompt is "PROMPT1#", Then you can define your
device as following::

    myDevice = linux.LinuxDevice("ssh://dev:1234@10.208.72.12",
                                 expect = "PROMPT1#")

Support it has different prompts in different mode, for example these are
"MODE1#" and "MODE2#", then we can define the device as::

    myDevice = linux.LinuxDevice("ssh://dev:1234@10.208.72.12",
                                 expect = ["MODE1#", "MODE2#"])

Then you can use the device as normal LinuxDevice.

5. An example
=============

In this example, we login the client linux device and then ftp the server.
Check if there is session generated on the test SRX firewall. Then tear
down the connection:

.. code-block:: python

    #!/usr/bin/env python
    from netdevice import cisco, junos, linux

    if __name__ == '__main__':
        dut = junos.JunosDevice("ssh://regress:1234@regazara.englab.test.net",
                root_password = "5678")
        client = linux.LinuxDevice("ssh://root:5678@ent-vm01.englab.test.net",
                interfaces = [ { 'name': 'eth1', 'inet': '1.1.1.2/24', 'inet6': '2001::2/64'} ])
        server = linux.LinuxDevice("ssh://root:5678@ent-vm02.englab.test.net",
                interfaces = [ { 'name': 'eth1', 'inet': '2.2.2.2/24', 'inet6': '2002::2/64'} ])

        client.cmd("ip route add 2.2.2.0/24 via 1.1.1.1 dev eth1")
        server.cmd("ip route add 1.1.1.0/24 via 2.2.2.1 dev eth1")
        dut.cli("clear security flow session application ftp")

        # connect to the server and list the files.
        client.cmd('ftp %s' %(server["interfaces"][0]["inet"].split('/')[0]), expect = "Name")
        client.cmd(server["username"], expect = "Password")
        client.cmd(server["password"], expect = "ftp")
        output = client.cmd('ls', expect = "ftp> ")
        if "226" in output:
            print("ftp output is shown.")
        else:
            print("ftp failed to connect the server.")

        # check the session and tear down the connection.
        sessions = dut.cli('show security flow session application ftp', parse = "flow-session")
        client.cmd('bye')

        if sessions and sessions[0]["flow-information"][0]['pkt-cnt'] > 0 and \
                sessions[0]["flow-information"][1]['pkt-cnt'] > 0:
            print("Session found, pass!")
        else:
            print("Failed to find the session")

6. Q/A
======

1) Why some command return timeout?

For time consuming command i.g. scp, ftp get command, please set the @timeout
properly to avoid the command timeout.

Please make sure there is no command timeout since the output of the last
command will messup the result of the next command.

If a command timeout, either send a CTRL + C to kill the current session:

    client.cmd("c", control = True)

or kill the current session and relogin the device to open a new session:

    client.relogin()

7. Changelog
============

1.0.0: Official release.

1.0.4: For ssh, add  -o GSSAPIAuthentication=no to accelerate the login process.

1.0.6: 1) When configure interface in junos, don't configure the zone.
    2) print the junos specific attritue in the init.
    3) remove some verbose log when login.

1.0.7: 1) Change or add the some private function: x_set_interface, x_set_zone, x_set_policy, besides, we won't commit the change after the functions, users must commit the change by his own.
    2) add the release version in each object, you can see what version the script run.

1.0.9: 1) Fix some bugs.

1.0.10: 1) Don't show the commit process in other thread. There are some issue on it.

1.1: support new device: ovs

1.2: support new device: ovn

1.2.1: 1) LinuxDevice support non server given, then it would run sh command locally.
       2) Support new device: ovn.

1.2.6 fix issue when login by telnet

1.3.2 Support send_tcp_packet() and send_udp_packet(), you can send any TCP/UDP packet via sendip(https://github.com/rickettm/SendIP).

1.3.3 1) The input expect parameter can be a list; 2) Bug fix: It might failed in the first ssh to the remote device. 3) Add some functions for easy use: login_ftp_server()/login_ssh_server()/login_telnet_server()/assert_value().

1.3.4 Bug fix: When expect is a list, it may fail to login.

1.3.5 Bug fix: fix some some typo in the document.

1.3.6 Bug fix: Sometimes when prompt is not given, it might failed to login.
