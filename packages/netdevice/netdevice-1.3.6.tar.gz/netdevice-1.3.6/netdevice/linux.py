#!/usr/bin/env python3
#coding=utf8
import sys, os, socket, re
import time, threading
import pexpect
import ipaddress
import collections
try:
    # Python 2.
    from StringIO import StringIO
    # Python 3.
except ImportError:
    from io import StringIO
#import json
import simplejson as json
import random
try:
    # Python 2.
    import urlparse
except ImportError:
    # Python 3.
    import urllib.parse as urlparse
import dpkt
import copy
from binascii import hexlify, unhexlify
from IPy import IP

LOG_EMERG = 0   # not used
LOG_ALERT = 1   # not used
LOG_CRIT = 2    # not used
LOG_ERR = 3     # Error message, maybe encounter error.
LOG_WARNING = 4 # + Warning message
LOG_NOTICE = 5  # + command
LOG_INFO = 6    # + command/output, it's the default level
LOG_DEBUG = 7   # + command/output/prompt staus, for debug
LOG_VERBOSE = 8 # + all above and pexpect log, for debug

color_dict = { 'blue': '\033[0;34m',
        'light_blue': '\033[1;34m',
        'green': '\033[0;32m',
        'light_green': '\033[1;32m',
        'cyan': '\033[0;36m',
        'light_cyan': '\033[1;36m',
        'red': '\033[0;31m',
        'light_red': '\033[1;31m',
        'purple': '\033[0;35m',
        'light_purple': '\033[1;35m',
        'brown': '\033[0;33m',
        'yellow': '\033[1;33m',
        'red_bold': '\033[01;31m',
        'light_gray': '\033[0;37m',
        'dark_gray': '\033[1;30m',
        'black': '\033[0;30m',
        'white': '\033[1;37m',
        'no_color': '\033[0m',
        }

bg_color_dict = {
        'no_color': '',
        'black': '\033[40m',
        'red': '\033[41m',
        'green': '\033[42m',
        'yellow': '\033[43m',
        'blue': '\033[44m',
        'purple': '\033[45m',
        'cyan': '\033[46m',
        'white': '\033[47m',
        }

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
                             # scheme/username/passowrd/host/port
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
    "LANG":       os.environ.get('LANG'),
    #"log_thread": True,     # record the log with thread name;

    # User can also define Whatever attributes you want.
    # ...
}

#class Result(object):
#    def __init__(self, msg, rc):
#        self.msg = msg
#        self.rc = rc
#        #setattr(self, "msg", msg)
#        #setattr(self, "rc", rc)
#    def __str__(self):
#        return "rc: %s, msg: %s" %(self.rc, self.msg)

class LinuxDevice(object):
    '''
    A base class for common linux devices.
    '''
    release = '1.3.5'

    LOG_EMERG = 0   # not used
    LOG_ALERT = 1   # not used
    LOG_CRIT = 2    # not used
    LOG_ERR = 3     # Error message, maybe encounter error.
    LOG_WARNING = 4 # + Warning message
    LOG_NOTICE = 5  # + command
    LOG_INFO = 6    # + command/output, it's the default level
    LOG_DEBUG = 7   # + command/output/prompt staus, for debug
    LOG_VERBOSE = 8 # + all above and pexpect log, for debug

    PROMPT_SET_SH = "PS1='[NETDEVICE]\$ '"
    PROMPT_SET_CSH = "set prompt='[NETDEVICE]\$ '"

    def __init__(self, server = None, **kwargs):
        """
        This is the constructor for LinuxDevice, The parameter pass the
        attribute that the object needs.

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
        """
        self.start_time = time.time()
        self.attributes = collections.OrderedDict()
        self.interface = collections.OrderedDict()
        self.connected = False
        self.random = random.randint(2, len(color_dict) - 5)

        if not self["type"]:
            self["type"] = 'Linux'
        # Parse the attribute, firstly the global configuration, then the
        # parameters, then the url parameters.
        #for k,v in default.iteritems():
        for k,v in default.items():
            self[k] = v
            if kwargs.get("log_level", 0) >= 8:
                print("default %s: %s" %(k, v))
        #for k,v in kwargs.iteritems():
        for k,v in kwargs.items():
            self[k] = v
            if kwargs.get("log_level", 0) >= 8:
                print("kwargs %s: %s" %(k, v))
        # back compatiable with "prompt = xxx" in old release.
        self["expect"] = self["expect"] and self["expect"] or self["prompt"]
        if self["expect"]:
            # Use user provided prompt at high priority
            if isinstance(self["expect"], list):
                self.prompt = self["expect"]
                self.original_prompt = self["expect"]
            else:
                self.prompt = [self["expect"]]
                self.original_prompt = [self["expect"]]
        else:
            # Used for the first match after login
            self.original_prompt = [r"[#$%>]"]
            self.prompt = ["\[NETDEVICE\][\$\#] "]

        if server or self["url"]:
            # Python 2.
            u = urlparse.urlparse(server and server or self["url"])
            q = urlparse.parse_qs(u.query)

            self["scheme"] = u.scheme
            self["username"] = u.username
            self["password"] = u.password
            self["hostname"] = u.hostname
            self["port"] = u.port
            #for k,v in q.iteritems():
            for k,v in q.items():
                self[k] = v

        self["log_color"] = self["log_color"] and self["log_color"] or list(color_dict.keys())[self.random]
        self.fd = self["log_file"] and open(self["log_file"], 'a+') or None

        # Used for log in login
        if self["name"]:
            self.name = self["name"]
        elif self.__is_ipaddress(self["hostname"]):
            self.name = self["hostname"]
            self["name"] = self.name
        elif self["hostname"]:
            self.name = self["hostname"].split(".")[0]
            self["name"] = self.name
        else:
            self.name = "Error"
            self["name"] = self.name

        self.log("welcome to %s device: %s, netdevice rev: %s.\n" %(self["type"],
            self["hostname"], self.release))
        if self["autologin"]:
            self.psession = self.login()
            self.connected = True
            self.name = LinuxDevice.cmd(self, "hostname",
                    log_level = self.LOG_WARNING).strip()
            self.__preconfig()
        #if self["type"] == 'Linux':
        #    tmp = copy.deepcopy(self.attributes)
        #    tmp["password"] = "*******"
        #    self.log("%s = %s\n" %(self.name, json.x_dumps(tmp, indent=4)))

        #self.x_get_interface()
        #self.log("interface = %s\n" %(json.x_dumps(self.interface, indent=4)))

    def __del__(self):
        '''
        Recycle resource when the object is destroied.
        '''
        # postconfig
        if self['postconfig']:
            for c in self['postconfig']:
                self.cmd(c)
        self.log("%s.%s, finish in %.2f seconds\n" %(self.__class__.__name__,
            sys._getframe().f_code.co_name,
            time.time() - self.start_time))
        #self.cmd('rm $INPUTRC', log_level = self.LOG_WARNING)
        #self.psession.close(force=True)

    def __getitem__(self, name):
        """
        Get members of the object.
        """
        return self.attributes.get(name, None)

    def __setitem__(self, name, value):
        """
        Set members to the object.
        """
        self.attributes[name] = value
        if not self.connected: 
            # If init not complete, only set the value
            return

        if name == "log_file":
            if self["log_file"] != None:
                close(self.fd)
                self.fd = -1
            if value != None:
                self.fd = open(value, 'w+')
        #elif name == "interfaces":
        #    self.del__configure_interface()

    def __cmd(self, cmd, expect = None, timeout = 20, background = False,
            logfile = "/dev/null", control = False,
            format = "output", log_command_leading = "\033[0;31m$ \033[0m",
            log_command_color = "no_color", log_command_bg_color = "no_color",
            log_output_color = "no_color", log_output_bg_color = "no_color",
            **kwargs):
        '''
        Execute a command provided by @cmd on remote Linuxdevice and return the
        execution result, If the @expect is found, it succeed and return
        immediately, or it will wait for at most @timeout seconds. The return
        result will be desginated by @format:
        
        @ expect: the prompt the execute is expected to include. If not
                  provided, the self.prompt is used. For some applications,
                  i.e ftp, it will not use the system's prompt so you must give
                  the expected prompt.

        @ timeout: Hong long to wait before it's thinked as timeout, if it
                   timeout a "CTRL + C" will be trriggered, so please set the
                   proper timeout carefully;

        @ background: Go to background immediately after startup.  If no output
                      file is specified via the -o, output is redirected to
                      /dev/null.

        @ logfile: Log all messages to logfile on the remote linux device.  The
                   messages are normally reported to standard error.

        @ control: If it is True, send a control character to the child such as
                   Ctrl-C or Ctrl-D. For example, to send a Ctrl-G (ASCII 7):: 

                       self.cmd('g', control = True)

        @ format: "output", it return the screen output.
                  "status", it return the execute status. i(>0) means it
                  execute successfully and match the i-th expected prompt.
                  "both", it return both of the above.

        @ log_command_leading: Which leading chars to add before command in the log.

        @ log_command_color: Which color to show the command in the log.

        @ log_command_bg_color: Which background color to show the command in the log.

        @ log_output_color: Which color to show the output in the log.

        @ log_output_bg_color: Which background color to show the output in the log.

        @ redirect: Noramlly the output would be shown on screen or log file,
                    if this is set then the output of the command would be
                    saved in the given file, it's especially useful for execute
                    command with big output. redirect = "/dev/null" would
                    redirect the output to a hole. For example:: 

                        pc.cmd("ifconfig", redirect = "ifconfig_result.log")

        [CAUTION]: please increase the timeout value if the command is
        time-consuming, or it will cause failure.
        '''

        prompt = [pexpect.EOF, pexpect.TIMEOUT]
        if not expect:
            prompt.extend(self.prompt)
        else:
            if isinstance(expect, list):
                prompt.extend(expect)
            else:
                prompt.append(expect)

        if background:
            cmd = cmd + ' > %s 2>&1 &' %(logfile)

        # Eat the prompt before send line.
        i = 2
        while i == 2:
            #self.log("cmd: %s, i: %d, prompt: %s.\n" %(cmd, i, prompt))
            i = self.psession.expect(prompt, 0.01)

        try:
            if control:
                self.psession.sendcontrol(cmd)
            else:
                self.psession.sendline(cmd)
        except Exception as e:
            # Maybe timeout for long time inactivity
            self.log("%s, reconnect the host.\n" %(e), level = LOG_WARNING, **kwargs)
            del self.psession
            self.psession = self.login()
            # Eat the prompt before send line.
            i = self.psession.expect(prompt, 0.01)
            self.log("re login match: %s\n" %(prompt[i]), level = LOG_DEBUG, **kwargs)
            self.log('succeed to re-connect to %s: %d\n' %(self["name"], i), **kwargs)
            # resend the command
            if control:
                self.psession.sendcontrol(cmd)
            else:
                self.psession.sendline(cmd)
            
        # Get the prompt
        self.log("%s\n" %(cmd),
                level = LOG_NOTICE,
                leading = log_command_leading,
                color = log_command_color,
                bg_color = log_command_bg_color,
                **kwargs)
        i = self.psession.expect(prompt, timeout)
        #self.log("cmd(2), i: %d\n" %(i))

        #status = (i >= 2) and True or False
        if self["log_level"] >= LOG_DEBUG:
            self.log("match result: %s, expect: %s\n" %(prompt[i], prompt[2]),
                    level = LOG_DEBUG, **kwargs)
            #self.log("result: %s\n" %(result), level = LOG_INFO)

        if i >= 2:
            #Succeed:
            # Prepare the output. Strip the line beofre the first '\r\n" since it
            # must be a command itself. Will correct it if encounter issue.
            #len1 = self.psession.before.find('%s' %(cmd))
            len1 = self.psession.before.find("\r\n")
            len2 = self.psession.before.rfind("\r\n")
            output = self.psession.before[len1:len2].strip("\r\n")
            # It's a bug workaround for the issues/669:
            output = re.sub(r"\x1b\[\?2004l\r", "", output)
            #print("cmd: %s, output: %s" %(cmd, output))
        else:
            #self.log('not see prompt in %ds, worng prompt? timeout?\n'
            #        %(timeout), level = LOG_WARNING,
            #        color = "light_red",
            #        **kwargs)
            output = ""
            #self.psession.sendeof()
            #self.psession.sendcontrol('c')
            #self.psession.sendcontrol('d')
            #i = self.psession.expect(" ", 1)
            #i = self.psession.expect(prompt, timeout)
            #self.log("Ctrl + C to cancel: %s\n" %(cmd))

        if kwargs.get("redirect", False):
            # If redirect option is set then don't log to stdout
            self.log("redirect the output to %s ...\n" %(kwargs["redirect"]))
            redirect_file = open(kwargs["redirect"], "w+")
            redirect_file.write(output + "\r\n\r\n")
            redirect_file.flush()
            redirect_file.close()
        else:
            self.log("%s" %(output),
                    level = 
                    (len(cmd.strip()) > 0 and cmd.strip()[-1] != "&") and
                    LOG_INFO or LOG_VERBOSE,
                    leading = "  ",
                    #color = output_color,
                    color = "dark_gray",
                    bg_color = log_output_bg_color,
                    **kwargs)

        if format == "output":
            #返回屏幕上的内容
            return output
        elif format == "status":
            #返回return code
            return i-2
        else:
            return (i-2, output)

    def __is_ipaddress (self, address):
        try:
            ip = ipaddress.ip_address(address)
        except Exception as e:
            #print(e)
            return False
        else:
            return True

    def __preconfig(self):
        '''
        call preconfig before test.
        '''
        if self["preconfig"]:
            if isinstance(self["preconfig"], list):
                for c in self["preconfig"]:
                    self.cmd(c)
            elif isinstance(self["preconfig"], str):
                f = StringIO(self["preconfig"])
                for c in f.readlines():
                    self.cmd(c.strip('[, ]'))
                f.close()

    def login(self, terminal_type = 'ansi', login_timeout = 10):
        '''
        Connect the object with the constructor attribute.

        The defualt attribute "autologin" is True, so normally it will be auto
        called. Set attribute "autologin" as False and you must call it
        explictly.
        '''
        if self["scheme"]  and self["username"] and self["hostname"]:
            cmd = self["scheme"]
            if (self["scheme"] == "ssh"):
                cmd += " -o GSSAPIAuthentication=no"
            cmd += ' -l %s %s' %(self["username"], self["hostname"])
            if self["port"]:
                if self["scheme"] == 'ssh':
                    cmd += ' -p'
                cmd += ' %d' %(int(self["port"]))
            self.log("%s\n" %(cmd))
        else:
            cmd = 'sh'
        psession = pexpect.spawn("%s" %(cmd), encoding='utf-8')
        self.psession = psession
        if self["log_level"] >= LOG_VERBOSE:
            psession.logfile = sys.stdout

        # For some host, it will prompt [#$%>] before login, for example
        # some host prompt "########## PDT PORTER VSRX INSTANCES
        # ###########" before login, it will be mis-treated as login
        # success. In such cases, users should give the prompt explicitly.
        prompt = ["(?i)Are you sure you want to continue connecting (yes/no/[fingerprint])?",
                "(?i)(?:password)|(?:passphrase for key)",
                "(?i)terminal type",
                "Escape character is",
                #"(?i)permission denied",
                "(?i)connection closed by remote host",
                pexpect.EOF,
                pexpect.TIMEOUT]
        prompt.extend(self.original_prompt)

        self.log("prompt: %s" %(prompt), level = LOG_DEBUG)
        i = psession.expect(prompt, timeout = login_timeout)
        self.log("login phase 1 match: %d/%s\n" %(i, prompt[i]), level = LOG_DEBUG)
        # Check if it's the first time to login
        if i==0: 
            # New certificate -- always accept it.
            psession.sendline("yes")
            #self.log("yes")
            i = psession.expect(prompt)

        # Check and input the password
        if i==1: # password or passphrase
            psession.sendline(self["password"])
            i = psession.expect(prompt)
        elif i==2:
            psession.sendline(terminal_type)
            i = psession.expect(prompt)
        elif i==3:
            psession.sendline("")
            i = psession.expect(prompt)

        self.log("login phase 2 match: %d/%s\n" %(i, prompt[i]), level = LOG_DEBUG)
        if i < 7:
            psession.close()
            error = (i < len(prompt)) and prompt[i] or "None"
            self.log('Login %s failed: %s' %(self["hostname"], error), color = "red")
            raise Exception ('Login %s failed: %s' %(self["hostname"], error))

        if (self["type"] == 'Junos'):
            # Second phase
            # For Junos device, enter shell and Eat the prompt before send line.
            # Since cmd() method might be overided, call the original one.
            LinuxDevice.cmd(self, "start shell", expect = self.original_prompt,
                    with_log = False, log_level = LOG_DEBUG)

        # need root privilage to configure the interface
        if self["username"] != "root" and self.attributes.get("root_password"):
            result = LinuxDevice.cmd(self, 'su', expect = '(?i)password:',
                    format = "status")
            if result >= 0:
                LinuxDevice.cmd(self, self["root_password"],
                        expect = self.original_prompt, log_level = LOG_DEBUG)

        if not self["expect"]:
            # self.prompt = ["\[NETDEVICE\][\$\#] "]
            # SUBTLE HACK ALERT! Note that the command to set the prompt uses a
            # slightly different string than the regular expression to match it. This
            # is because when you set the prompt the command will echo back, but we
            # don't want to match the echoed command. So if we make the set command
            # slightly different than the regex we eliminate the problem. To make the
            # set command different we add a backslash in front of $. The $ doesn't
            # need to be escaped, but it doesn't hurt and serves to make the set
            # prompt command different than the regex.
            #
            # if you 'su' to a different user then you will need to manually reset
            # the prompt. This sends shell commands to the remote host to set the
            # prompt, so this assumes the remote host is ready to receive commands. 
            result = LinuxDevice.cmd(self, self.PROMPT_SET_SH, format = "status",
                    timeout=1, with_log = False, log_level = self.LOG_DEBUG)
            if result <= 0:
                LinuxDevice.cmd(self, self.PROMPT_SET_CSH, format = "status",
                                    timeout=1, with_log = False,
                                    log_level = self.LOG_DEBUG)
        self.connected = True
        return psession

    def relogin(self):
        '''
        Kill the current session and relogin.
        '''
        self.log("relogin.\n")
        del self.psession
        self.psession = self.login()

    # mutile command in one function:
    def cmd (self, *args, **kwargs):
        '''
        Execute a command and return the result of the last command. the
        result include the output(msg) and return code(rc):

            * msg: the output in the screen.
            * rc: return code, <0 means failure or timeout, 0 means
              match the 1st expected value, 1 means match the 2nd expected
              value, etc...

        For examples::

            (output, rc) = pc1.cmd("ls", format = "both")
            pc1.assert_value(rc >= 0, "")
            self.log(output)
        '''
        result = ""
        cmdlist = []
        for cmd in args:
            if isinstance(cmd, list):
                cmdlist.extend(cmd)
            else:
                cmdlist.append(cmd)
        for cmd in cmdlist:
            for c in StringIO(cmd.strip()).readlines():
                if c.strip() and c.strip()[0] != '#':
                    result = self.__cmd(c.strip(), **kwargs)
                    #print("result: %s" %(result))
        return result

    def thread(self, group=None, target=None, name=None, args=(), kwargs={}):
        '''
        To be implemented.
        refer to: http://www.cnblogs.com/fnng/p/3670789.html
        Open a new thread and execut the command.
        '''

        t = threading.Thread(group=group, target=target, name = name, args=args, *kwargs)
        t.setDaemon(True)
        t.start()
        return t

    def log (self, message, level = LOG_NOTICE, leading = None, color =
            "no_color", bg_color = "no_color", log_level = None, **kwargs):
        '''
        record the log to file self["log_file"] with the color
        self["log_color"], with the local time if self['log_time'] is True,
        the log looks like::

            [2017-05-16 16:02:07][ regazara ]: ssh login succeed.

        @ message: The log text.

        @ level: The log level of the text. Will not show if it's large than
        the self["log_level"].

        @log_level: will override the level

        @ color: The log color of the text.

        @ bg_color: The log background color of the text.

        '''
        log_level = log_level and log_level or self["log_level"]
        #print("level: %d, log_level: %d" %(level, log_level))
        if level > log_level or (not kwargs.get("with_log", True)):
            return

        name_color = color_dict.get(self['log_color'], None)
        now = time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))
        l = self['log_time'] and "[%s]" %(now) or ""
        #l += "[%s][%s]" %(now, threading.current_thread().name)
        if kwargs.get("log_name", None):
            logname = kwargs["log_name"]
        else:
            logname = self["name"]
        l2 = l + "[%s%s%s]" %(name_color and name_color or "",
                logname, name_color and "\033[0m" or "")

        f = StringIO(message)
        for i in f.readlines():
            # remove the trailing '\n' and readd later.
            i = i.strip('[\r\n]')
            if color != "no_color" or bg_color != "no_color":
                i = "%s%s%s%s" %(color_dict.get(color, 'no_color'),
                        bg_color_dict.get(bg_color, 'no_color'),
                        i, color_dict['no_color'])
            if leading:
                i = leading + i
            if self.fd:
                self.fd.write("%s: %s\n" %(l2, i))
                self.fd.flush()
            sys.stdout.write("%s: %s\n" %(l2, i))
        f.close()

    def sleep (self, timeout, total = 50, char = '>', description = "sleep"):
        '''
        Sleep with progress bar, the granularity is 0.1 second. something like
        that:

        sleep 7/10[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>               ][71%]

        '''

        count = int(timeout * 10)
        ratio = float(total) / count
        self.log("%s %d seconds" %(description, timeout))
        # You can use this flag to run as a thread
        self.terminate_loop = False
        for i in range(1, count + 1):
            progress = int(i * ratio)
            str = char * progress + ' ' * (total - progress)
            sys.stdout.write('\r%s %s/%s[%s][%d%%]'%(description, i/10, timeout,
                str, i * 100 / count))
            sys.stdout.flush()
            time.sleep(0.1)
            if self.terminate_loop:
                # After it start, you can set self.terminate_loop = True to terminate it.
                break
        sys.stdout.write('\r\n')
        sys.stdout.flush()

    def test_color (self):
        '''
        print the color name in the color.
        '''
        print("Supported color: ")
        for k,v in color_dict.iteritems():
            print("    %s %s \033[0m" %(v, k))

    def assert_value(self, value, msg, **kwargs):
        '''
        Assert and throw exception if False.
        '''
        if value:
            self.log("SUCCEED: %s" %(msg),
                    color = kwargs.get("success_color", "green"))
        else:
            self.log("FAILED: %s" %(msg),
                    color = kwargs.get("fail_color", "red"))
            raise Exception(msg)

    def get_file(self, filename, localname = '.', scheme = "scp", timeout = -1):
        '''
        Get file from current host by scp.

        @filename: file to get from the host.

        @localname: save name after download

        @timeout: How long to wait for the files to be downloaded. Default is
        neveer timeout
        '''
        cmd = 'scp -o GSSAPIAuthentication=no %s@%s:%s %s' %(self["username"], self["hostname"], filename, localname)
        self.log(cmd, leading = "\033[0;31m$ \033[0m",)
        clild = pexpect.spawn(cmd)
        if self["log_level"] >= LOG_VERBOSE:
            clild.logfile = sys.stdout

        prompt = [pexpect.EOF,
                pexpect.TIMEOUT,
                "(?i)are you sure you want to continue connecting",
                "(?i)password:",
                "ETA"]
        while True:
            i = clild.expect(prompt, timeout)
            if i == 1:
                #print("timeout")
                break
            elif i == 2:
                clild.sendline ('yes')
            elif i == 3:
                clild.sendline ('%s' %(self["password"]))
            elif i == 4:
                sys.stdout.write("\r%s %s" %(clild.before, clild.after))
                sys.stdout.flush()
            else:
                break
        sys.stdout.write("\r\ndownload complete\r\n")
        sys.stdout.flush()
        self.log("download complete\n")

    def put_file(self, filename, remotedir, timeout = -1):
        '''
        put file to current host by scp.

        @filename: file to put from the local. local means the host where you
        execute this scriopt.

        @remotedir: save name after upload.

        @timeout: How long to wait for the files to be uploaded. If the file
        is very big, set it to a big value or it will fail.
        '''
        self.log("upload: %s@%s:%s <- %s\n" %(self["username"], self["hostname"],
            remotedir, filename), leading = "\033[0;31m$ \033[0m",)
        clild = pexpect.spawn('scp -o GSSAPIAuthentication=no %s %s@%s:%s' %(filename, self["username"],
            self["hostname"], remotedir))
        prompt = [pexpect.EOF,
                pexpect.TIMEOUT,
                "(?i)are you sure you want to continue connecting",
                "(?i)password:",
                "ETA"]
        while True:
            i = clild.expect(prompt, timeout)
            if i == 1:
                #print("timeout")
                break
            elif i == 2:
                clild.sendline ('yes')
            elif i == 3:
                clild.sendline ('%s' %(self["password"]))
            elif i == 4:
                sys.stdout.write("\r%s %s" %(clild.before, clild.after))
                sys.stdout.flush()
            else:
                break
        sys.stdout.write("\r\nupload complete\r\n")
        sys.stdout.flush()
        self.log("upload complete\n")

    def get_files (self, *args, **kwargs):
        '''
        Get files from current host by scp.
        '''
        for arg in args:
            self.get_file(arg, **kwargs)

    def send_udp_packet (self, data = b'', sip = '192.168.1.2', dip = '192.168.2.2',
            sport = 4000, dport = 5000, **kwargs):
        '''
        Generate a UDP packet and send it using sendip. You must install
        sendip at first.

        Example::

            pc1.send_udp_packet("A test.", sip = pc1_ip, dip = pc2_ip,
                    sport = 4000, dport = 5000)
        '''
        #UDP header
        if isinstance(data, bytes) or (not data):
            payload = data
        else:
            payload = bytes(data, encoding='utf8')
        udp = dpkt.udp.UDP(sport = sport, dport = dport, sum = 0, data = payload)
        udp.ulen = len(udp)
        #udp.sum = 0 # Force to recaculate the checksum
        #self.log("udp: %s" %(bytes(udp).hex()))

        # IP header
        if ':' in sip or ':' in dip:
            ip = dpkt.ip6.IP6(id=0,
                    src = socket.inet_pton(socket.AF_INET, sip),
                    dst = socket.inet_pton(socket.AF_INET, dip),
                    p=dpkt.ip.IP_PROTO_UDP, data = udp)
            family = socket.AF_INET6
        else:
            ip = dpkt.ip.IP(id=0,
                    src = socket.inet_pton(socket.AF_INET, sip),
                    dst = socket.inet_pton(socket.AF_INET, dip),
                    p=dpkt.ip.IP_PROTO_UDP, data = udp)
            family = socket.AF_INET
        ip.len += len(ip.data)
        ip.sum = 0 # Force to recaculate the checksum
        ip.data.sum = 0 # Force to recaculate the checksum

        target = kwargs.get("target", None) and kwargs["target"] or dip
        self.log('sendip to %s: %s:%s --> %s:%s;%s' %(target, sip, sport, dip,
            dport, dpkt.ip.get_ip_proto_name(ip.p)))
        self.log(repr(ip), leading = '    ')
        self.cmd("sendip %s -d '0x%s'" %(target, bytes(ip).hex()))

    def send_tcp_packet (self, data = b'', sip = '1.1.1.2', dip = '2.2.2.2',
            sport = 4000, dport = 5000, seq = 0, ack = 1, off = 0,
            flags = dpkt.tcp.TH_PUSH | dpkt.tcp.TH_ACK,
            win = 8760, sum = 0, urp = 0, opts = b'', **kwargs):
        '''
        Generate a TCP packet and send it using sendip. You must install
        sendip at first.

        Attributes:
            sport - source port(16),    dport - destination port(16)
            seq   - sequence number(32)
            ack   - acknowledgement number(32)
            off   - data offset, flags - TCP flags, win - TCP window size
            sum   - checksum(16),       urp   - urgent pointer(16)
            opts  - TCP options buffer; call parse_opts() to parse

        Example::

            pc1.send_tcp_packet(sip = pc1_ip, dip = pc2_ip, sport = 5000,
                    dport = 5001, seq = 0, ack = 0, flags = 0x02)
        '''
        #TCP header
        if isinstance(data, bytes) or (not data):
            payload = data
        else:
            payload = bytes(data, encoding='utf8')
        tcp = dpkt.tcp.TCP(sport = sport, dport = dport, seq = seq, ack = ack,
                off = off, flags=flags, win = win, sum = sum, urp = urp,
                opts = opts, data = payload)
        #tcp.ulen = len(udp)
        #self.log("tcp: %s" %(bytes(tcp).hex()))
        #self.log("tcp: %s" %(repr(tcp)))

        # IP header
        if ':' in sip or ':' in dip:
            ip = dpkt.ip6.IP6(id=0,
                    src = socket.inet_pton(socket.AF_INET6, sip),
                    dst = socket.inet_pton(socket.AF_INET6, dip),
                    p=dpkt.ip.IP_PROTO_TCP, data = tcp)
            family = socket.AF_INET6
        else:
            ip = dpkt.ip.IP(id=0,
                    src = socket.inet_pton(socket.AF_INET, sip),
                    dst = socket.inet_pton(socket.AF_INET, dip),
                    p=dpkt.ip.IP_PROTO_TCP, data = tcp)
            family = socket.AF_INET
        ip.len += len(ip.data)
        ip.sum = 0 # Force to recaculate the checksum
        ip.data.sum = 0 # Force to recaculate the checksum
        #self.log("ip: %s" %(bytes(ip).hex()))
        #self.log("ip: %s" %(repr(ip)))

        target = kwargs.get("target", None) and kwargs["target"] or dip
        self.log('sendip to %s: %s:%s --> %s:%s;%s' %(target, sip, sport, dip,
            dport, dpkt.ip.get_ip_proto_name(ip.p)))
        self.log(repr(ip), leading = '    ')
        self.cmd("sendip %s -d '0x%s'" %(target, bytes(ip).hex()))

    def login_ftp_server (self, server, expect = "ftp>", *args, **kwargs):
        '''
        print the color name in the color.
        '''
        username = kwargs.get("username", None) \
                and kwargs["username"] or self["username"]
        password = kwargs.get("password", None) \
                and kwargs["password"] or self["password"]
        if kwargs.get("port", None):
            cmd = 'ftp %s %d' %(server, kwargs["port"])
        else:
            cmd = 'ftp %s' %(server)

        result = self.cmd(cmd, expect = 'Name', format = "status")
        if result < 0:
            self.log("failed to find Name prompt.\n", color = 'red')
            return result

        result = self.cmd(username, expect = '[P|p]assword', format = "status")
        if result < 0:
            self.log("failed to find password prompt.\n", color = 'red')
            return result

        result = self.cmd(password, expect = expect, format = "status")
        if result < 0:
            self.log("failed to find %s prompt.\n" %(expect), color = 'red')
            return result

        return result

    def login_ssh_server (self, server, expect, *args, **kwargs):
        '''
        print the color name in the color.
        '''
        username = kwargs.get("username", None) \
                and kwargs["username"] or self["username"]
        password = kwargs.get("password", None) \
                and kwargs["password"] or self["password"]

        #删除ssh历史记录避免提示man-in-the-middle attack
        self.cmd('sed -i "/^%s/d" ~/.ssh/known_hosts' %(server))

        #print("kwargs: %s" %(kwargs))
        #print("username: %s" %(username))
        if kwargs.get("port", None):
            cmd = 'ssh -p %d %s@%s' %(kwargs["port"], username, server)
        else:
            cmd = 'ssh %s@%s' %(username, server)

        #expect 有两个值，需要分别处理两种返回值的情况
        ssh_prompt = ["(?i)Are you sure you want to continue connecting (yes/no/[fingerprint])?",
                'password:']
        result = self.cmd(cmd, expect = ssh_prompt, format = "status")
        if result < 0:
            self.log("failed to find password prompt.\n", color = 'red')
            return result
        elif result == 0:
            #match the first prompt
            result = self.cmd("yes", expect = 'password:', format = "status")

        result = self.cmd(password, expect = expect, format = "status")
        if result < 0:
            self.log("failed to find %s prompt.\n" %(expect), color = 'red')
            return result

        return result

    def login_telnet_server (self, server, expect, *args, **kwargs):
        '''
        print the color name in the color.
        '''
        username = kwargs.get("username", None) \
                and kwargs["username"] or self["username"]
        password = kwargs.get("password", None) \
                and kwargs["password"] or self["password"]

        #print("kwargs: %s" %(kwargs))
        #print("username: %s" %(username))
        if kwargs.get("port", None):
            cmd = 'telnet %s %d' %(server, kwargs["port"])
        else:
            cmd = 'telnet %s' %(server)

        result = self.cmd(cmd, expect = 'login:', format = "status")
        if result < 0:
            self.log("failed to find login prompt.\n", color = 'red')
            return result

        result = self.cmd(username, expect = 'password:', format = "status")
        if result < 0:
            self.log("failed to find password prompt.\n", color = 'red')
            return result

        result = self.cmd(password, expect = expect, format = "status")
        if result < 0:
            self.log("failed to find %s prompt.\n" %(expect), color = 'red')
            return result

        return result

    #def login_https_server (self, server, expect, *args, **kwargs):
    #    '''
    #    print the color name in the color.
    #    '''
    #    print("Supported color: ")
    #    for k,v in color_dict.iteritems():
    #        print("    %s %s \033[0m" %(v, k))

    def reboot (self):
        '''
        reboot the box
        '''
        try:
            self.psession = self.cmd("reboot")
        except Exception as e:
            print(e)

        # reconnect to the object after reboot
        del self.psession
        self.sleep(60)
        while True:
            try:
                self.psession = self.login()
            except Exception as e:
                self.sleep(60)
            else:
                self._enter_configure_mode()
                break
        self.log("system is up.\n")

    def x_sendip (self, pkt, src = None, dst = None, sport = None, dport = None):
        '''
        Experiment:

        Replay the packet like tcpreplay on the linux box. The packet should
        include the ip header + tcp/udp header + payload in hex format.
        Currently only support UDP and TCP, for example:

        0x4500003077e240008006a5a50ac645c70aa8820b049f00154e372b0e
        000000007002ffff27e60000020405b401010402

        @pkt: the packet in hex plain text format including the ip header;
        @src: replace the source ip addrss in the @pkt if not None
        @dst: replace the destination ip addrss in the @pkt if not None
        @sport: replace the source port in the @pkt if not None
        @dport: replace the destination port in the @pkt if not None

        ipv6 header format:
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |Version| Traffic Class |           Flow Label                  |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |         Payload Length        |  Next Header  |   Hop Limit   |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                                                               |
        +                                                               +
        |                                                               |
        +                         Source Address                        +
        |                                                               |
        +                                                               +
        |                                                               |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                                                               |
        +                                                               +
        |                                                               |
        +                      Destination Address                      +
        |                                                               |
        +                                                               +
        |                                                               |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Examples:
            sync = '45 00 00 30 77 e2 40 00 80 06 a5 a5 0a c6 45 c7
                    0a a8 82 0b 04 9f 00 15 4e 37 2b 0e 00 00 00 00
                    70 02 ff ff 27 e6 00 00 02 04 05 b4 01 01 04 02'
            client.x_sendip(syn, src = "1.1.1.2", dst = "2.2.2.2",
                             sport = 12222, dport = 80)

        sendip has bug in send ipv6 packet with -d pamaters. This is the fix:

        RCS file: /home/ypguo/.cvsroot/sendip/sendip.c,v
        retrieving revision 1.1.1.1
        diff -u -p -r1.1.1.1 sendip.c
        --- sendip.c	3 Jan 2018 04:02:31 -0000	1.1.1.1
        +++ sendip.c	3 Jan 2018 04:04:29 -0000
        @@ -686,9 +686,14 @@ int main(int argc, char *const argv[]) {
                                        free(packet.data);
                                        unload_modules(FALSE,verbosity);
                                        return 1;
        -			} else {
        -				af_type = AF_INET;
        -			}
        +            } else {
        +                if (strchr(argv[gnuoptind], ':')) {
        +                    /* the destination address is ipv6 address. */
        +                    af_type = AF_INET6;
        +                } else {
        +                    af_type = AF_INET;
        +                }
        +            }


        '''
        # First of all, format a ip/ipv6 packet.
        pkt = "".join(pkt.replace("0x", "").split()) # remove the \s in the string.
        if pkt[0] == '6':
            ip = dpkt.ip6.IP6(unhexlify(pkt))
            self.log('v: 0x%x, fc: 0x%x, flow: 0x%x, src: %s, dst: %s, nxt: %d, plen: %d' %(ip.v,
                ip.fc, ip.flow, socket.inet_ntop(socket.AF_INET6, ip.src),
                socket.inet_ntop(socket.AF_INET6, ip.dst), ip.nxt, ip.plen))
        elif pkt[0] == '4':
            ip = dpkt.ip.IP(unhexlify(pkt))
        family = (ip.v == 6) and socket.AF_INET6 or socket.AF_INET
        if (ip.p not in [1, 58, 6, 17]):
            self.cmd("x_sendip() only support TCP/UDP/ICMP/ICMPV6 now")
            return

        # Secondly, replace the src, dst, sport, dpot in the pkt.
        ip.sum = 0 # Force to recaculate the checksum
        ip.data.sum = 0 # Force to recaculate the checksum
        ip.src = socket.inet_pton(family, src) if src else ip.src
        ip.dst = socket.inet_pton(family, dst) if dst else ip.dst
        ip.data.sport = sport if sport else ip.data.sport
        ip.data.dport = dport if dport else ip.data.dport

        self.log('%s:%d --> %s:%d;%d, ip_len: %d' %(socket.inet_ntop(family, ip.src),
            ip.data.sport, socket.inet_ntop(family, ip.dst), ip.data.dport,
            ip.p, (family == socket.AF_INET6) and ip.plen or ip.len))
        packet = "%s" %(bytes(ip).hex())
        self.log("packet: %s" %(packet))
        self.log("packet[1:]: %s" %(packet[1:]))
        self.log("packet[2:]: %s" %(packet[2:]))
        self.cmd("sendip %s -d '0x%s'" %(socket.inet_ntop(family, ip.dst),
            bytes(ip).hex()))

    def x_tcpreplay (self, remote, filename, saddr = None, sport = None,
            daddr = None, dport = None, proto = None, replay_range = None):
        '''
        Experiment:

        Replay the packet capture file @filename by sendip, the file could be
        collected by tnpdump or wireshark.

        @remote: the server which is linuxdevice object.
        @filename: the packet capture file.
        @saddr: the client address in the packet capture.
        @daddr: the server address in the packet capture.
        @sport: the client port in the packet capture.
        @dport: the server port in the packet capture.
        @port: the protol that to be replayed in the packet capture.
        @replay_range: the list of frame number to be replayed in the packet capture.
        '''

        fd = open(filename, 'rb')

        # Prepare the filter: If there is no client and server desginated,
        # guess who is the client: 1) For TCP packet, who send the SYN.
        if not saddr and not sport and not daddr and not dport:
            pcap = dpkt.pcap.Reader(fd)
            for ts, buf in pcap:
                eth = dpkt.ethernet.Ethernet(buf)
                if isinstance(eth.data, dpkt.ip.IP) or isinstance(eth.data, dpkt.ip6.IP6):
                    ip = eth.data
                    #print hexlify(str(ip))
                    if ip.p == 6 and ip.data.flags == 0x02:
                        saddr = IP(int(hexlify(ip.src), 16))
                        #print str(saddr)
                        break
            if not saddr and not sport and not daddr and not dport:
                print("at least desginate one filter to select the direction.")
                return
            fd.seek(0,0)
        #match = self._filter_match(ip, saddr, sport, daddr, dport, proto)
        saddr_set = saddr and IP(saddr) or None
        sport = sport and int(sport) or None
        daddr_set = daddr and IP(daddr) or None
        dport = dport and int(dport) or None
        proto = proto and int(proto) or None

        iptable_cmd = (saddr.version() == 6) and "ip6tables" or "iptables"
        local = self
        client_addr = (saddr.version() == 6) and str(local.interfaces[0]["inet6"].ip) or str(local.interfaces[0]["inet"].ip)
        server_addr = (saddr.version() == 6) and str(remote.interfaces[0]["inet6"].ip) or str(remote.interfaces[0]["inet"].ip)
        # To avoid to generating the RST/ICMP error.
        local.cmd("%s -I INPUT -s %s -j DROP" %(iptable_cmd, server_addr))
        remote.cmd("%s -I INPUT -s %s -j DROP" %(iptable_cmd, client_addr))

        flag = 0
        f = 0
        self.log('replaying the packet...')
        self.log(' No.      time,  ipid,    src ip:port,   dst ip:port, protocol')
        self.log('===================================================')
        pcap = dpkt.pcap.Reader(fd)
        for ts, buf in pcap:
            if (flag == 0):
                t0 = ts
                t1 = ts
                flag = 1

            f += 1
            t1 = ts
            if (replay_range and f not in replay_range):
                # Only replay the packet in the @replay_range
                continue

            time.sleep(ts - t1)
            eth = dpkt.ethernet.Ethernet(buf)
            if not isinstance(eth.data, dpkt.ip.IP) and not isinstance(eth.data, dpkt.ip6.IP6):
                self.log('%4d %11f non-ip packet' %(f, ts - t0, ))
                continue
            ip = eth.data

            ipsrc = IP(int(hexlify(ip.src), 16))
            ipdst = IP(int(hexlify(ip.dst), 16))
            match = 0
            if (not proto or proto == ip.p) and\
                    (not saddr_set or ipsrc in saddr_set) and\
                    (not daddr_set or ipdst in daddr_set) and\
                    (not sport or sport == ip.data.sport) and\
                    (not dport or dport == ip.data.dport):
                s = client_addr
                d = server_addr
                v = local
            elif (not proto or proto == ip.p) and\
                    (not saddr_set or ipdst in saddr_set) and\
                    (not daddr_set or ipsrc in daddr_set) and \
                    (not sport or sport == ip.data.dport) and\
                    (not dport or dport == ip.data.sport):
                s = server_addr
                d = client_addr
                v = remote
            else:
                continue
            
            ip.src = socket.inet_pton((saddr.version() == 6) and socket.AF_INET6 or socket.AF_INET, s)
            ip.dst = socket.inet_pton((saddr.version() == 6) and socket.AF_INET6 or socket.AF_INET, d)
            ip.sum = 0 # Force to recaculate the checksum
            ip.data.sum = 0 # Force to recaculate the checksum
            v.cmd("sendip -d '0x%s' %s" %(hexlify(str(ip)), d), log_level = LOG_DEBUG)
            tcpflags = (ip.p == 6) and "[0x%x]" %(ip.data.flags) or ""
            self.log('%4d %11f %15s:%5d --> %15s:%5d;%d, %s len: %d' %(f, ts - t0,
                s, ip.data.sport, d, ip.data.dport, ip.p, tcpflags,
                (saddr.version() == 6) and ip.plen or ip.len))
        local.cmd("%s -F" %(iptable_cmd))
        remote.cmd("%s -F" %(iptable_cmd))

    def x_set_interface (self, *args):
        """
        Experiment:

        configure the interface with the given parameters.
        The interface looks like this, you can configure multi interfaces in
        one time, for examples:

        client.x_set_interface("eth1", "41.0.0.2", "2002::2")
        client.x_set_interface(name = "eth1", inet = "41.0.0.2", inet6 = "2002::2")

        """
        #print "%s.%s invoked" %(self.__class__.__name__, sys._getframe().f_code.co_name)
        for arg in args:
            if isinstance(arg, dict):
                if ('name' in arg.keys()):
                    self.cmd("ip address flush dev %s" %(arg["name"]))
                    if ('inet' in arg.keys()):
                        self.cmd("ip address add %s dev %s" %(arg["inet"], arg["name"]))
                    if ('inet6' in arg.keys()):
                        self.cmd("ip -6 address add %s dev %s" %(arg["inet6"], arg["name"]))
                    self.interface[arg["name"]] = arg
            elif isinstance(arg, tuple):
                # Easy mode
                self.cmd("ip address flush dev %s" %(arg[0]))
                self.cmd("ip address add %s dev %s" %(arg[1], arg[0]))
                self.cmd("ip -6 address add %s dev %s" %(arg[2], arg[0]))
                self.interface[arg["name"]]["name"] = arg[0]
                self.interface[arg["name"]]["inet"] = arg[1]
                self.interface[arg["name"]]["inet6"] = arg[2]
        #self.log("interface changes: %s\n" %(json.x_dumps(args, indent=4)))

    def x_set_route (self, local, gateway, remote):
        """
        Experiment:

        Re-configure the interface with the given parameters, for examples:

        #int0 = { 'name': 'eth1', 'inet': '41.0.0.2/24', 'inet6': '2001::2/64'}
        client.x_set_route(client["int0"], dut["int0"], server["int0"])

        """
        #print "%s.%s invoked" %(self.__class__.__name__, sys._getframe().f_code.co_name)

        if not local or not gateway or not remote:
            self.log("local or gateway or remote is None")
            return
        if 'name' in local.keys() and 'inet' in gateway.keys() and 'inet' in remote.keys():
            lname = local["name"]
            r = ipaddress.ip_interface(remote["inet"])
            g = ipaddress.ip_interface(gateway["inet"])
            self.cmd("ip route delete %s" %(r.network))
            self.cmd("ip route add %s via %s dev %s" %(r.network, g.ip, lname))

        if 'name' in local.keys() and 'inet6' in gateway.keys() and 'inet6' in remote.keys():
            lname = local["name"]
            r = ipaddress.ip_interface(remote["inet6"])
            g = ipaddress.ip_interface(gateway["inet6"])
            self.cmd("ip -6 route delete %s" %(r.network))
            self.cmd("ip -6 route add %s via %s dev %s" %(r.network, g.ip, lname))

    def x_interfaces (self, name):
    #def __getattr__
        '''
        Experiment:

        Get interface configuration given a interface name.
        '''
        results = self.cmd("ip address show %s" %(name), with_log = False)
        print(results.msg)
        print("------")
        for i in StringIO(results.msg).readlines():
            if i.startswith('    '):
                print(i)
                #print i.split()
        return

    def x_dumps(self):
        '''
        Experiment:

        Dump all its attributes.
        '''
        self.log("attributes: %s" %(json.x_dumps(self.attributes, indent=4)))
        #for k,v in self.attributes.iteritems():
        #    if "int" in k:
        #        print "    %s: %s \033[0m" %(k, v)
        self.log('"prompt": %s' %(self.prompt))
        self.log('"connected": %s' %(self.connected))
        self.log('"start_time": %s' %(time.strftime('%Y%m%d %H:%M:%S', time.localtime(self.start_time))))

    def x_get_interface (self, name = None):
        '''
        Experiment:

        Get interface configuration given a interface name.
        '''
        #results = self.cmd("ip address show dev %s" %(name), with_log = False)
        results = self.cmd("ip address show", with_log = False)
        f = StringIO(results)
        for i in f.readlines():
            if "mtu" in i:
                # A new interface
                name = i.split()[1].strip(":")
                self.interface[name] = collections.OrderedDict()
                self.interface[name]["name"] = name
            elif i.startswith('    '):
                family = i.split()[0].split('/')[0]
                self.interface[name][family] = i.split()[1]
        return self.interface

    def x_get_interfaces3 (self, name):
        '''
        Experiment:

        Get interface configuration given a interface name.
        '''

        interface = collections.OrderedDict()

        results = self.cmd("ip address show dev %s" %(name), with_log = False)
        f = StringIO(results)
        for i in f.readlines():
            if " state " in i:
                # A new interface
                name = i.split()[1].strip(":")
                interface["name"] = name
                interface["inet"] = []
                interface["link"] = []
                interface["inet6"] = []
            elif "inet " in i:
                #interface["inet"].append(i.split()[1])
                interface["inet"].append(ipaddress.ip_interface(i.split()[1]))
            elif "inet6 " in i:
                #interface["inet6"].append(i.split()[1])
                interface["inet6"].append(ipaddress.ip_interface(i.split()[1]))
            elif "link/ether " in i:
                interface["link"].append(i.split()[1])

        return interface


    def x_ip_address_add (self, name, ip = None, ip6 = None):
        """
        Experiment:

        ip address add "ip" dev "name"
        """
        #ip = ipaddress.ip_address(address)
        self.cmd("ip address flush dev %s" %(name))
        if ip:
            self.cmd("ip address add %s dev %s" %(ip, name))
        if ip6:
            self.cmd("ip -6 address add %s dev %s" %(ip6, name))
        self.cmd("ip link set %s up" %(name))

    def x_ip_address_show (self, ifname, family = 4, host = None, hosttype = None):
        """
        Experiment:

        ip show ifname on device host(type: hosttype)
        """
        if host and hosttype == "kvm":
            if family == 4:
                ip = self.cmd("ssh %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
            else:
                ip = self.cmd("ssh %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
        elif host and hosttype == "netns":
            if family == 4:
                ip = self.cmd("ip netns exec %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
            else:
                ip = self.cmd("ip netns exec %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
        elif host and hosttype == "container":
            if family == 4:
                ip = self.cmd("docker exec -it %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
            else:
                ip = self.cmd("docker exec -it %s ip -o -4 addr list %s | awk '{print $4}'"
                        %(host, ifname))
        else: # Get the ip on the linux host
            if family == 4:
                ip = self.cmd("ip -o -4 addr list %s | awk '{print $4}'"
                        %(ifname))
            else:
                ip = self.cmd("ip -o -4 addr list %s | awk '{print $4}'"
                        %(ifname))
        #return ipaddress.ip_interface(ip.strip()).ip
        return ip.split("\n")[0]

if __name__ == '__main__':
    dut = linux.LinuxDevice(url = "ssh://root:a1b2c3d4@1@192.168.200.49",
            expect = ["TEST1#", "TEST1\[DBG\]#"],
            preconfig = ["pwd", "ps"])
    print(dut.cmd("ifconfig"))

