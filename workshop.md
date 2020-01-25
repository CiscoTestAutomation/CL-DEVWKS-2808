# DEVWKS-2808 Main Workshop Content

NetDevOps revolves around the concept of being able to automatically and 
continuously design, develop, deploy, and more importantly, validate and verify 
your changes were successful, and that the expected outcomes are seen.

In this workshop, we'll dive deep into the world of Python programming with 
Cisco pyATS/Genie, and learn about: 

1. how to represent your testbed devices and its topology in YAML
2. connect to the devices
3. parse your device outputs
4. profile your device features
5. and build a full-on script!

## Mocked Testbed/Devices

Because this workshop is intended for classroom audience (and at home users DIY
on their own laptop/environment), we will be leveraging pyATS Unicon mock device
technology - it doesn't require real devices, but "emulates" pre-recorded
device interactions (eg, `show` commands).

Eg: lines starting with `command: mock_device_cli` instructs the infrastructure
to use mock devices (or to be more precise, start a connection using this 
mock command instead of real telnet/ssh etc).

There are a series of limitations with mock devices (eg, you cannot configure 
them, and their interactions are limited to a pre-defined set of recordings), 
but should suffice for the workshop training.

If you have devices to tinker with (eg, VIRL or your own lab devices), feel 
free to use your own host/ip/credentials, and remove the `command:` line.


## Step 1: Defining a Testbed YAML File

Automation revolves around being able to programmatically establish connection
to your testbed devices. To do that, we need to first "describe" what devices
we have, and "how" to connect to them. In the pyATS ecosystem, this is done 
using a testbed file. 

Testbed files leverage [YAML](https://yaml.org/spec/1.2/spec.html) syntax to
describe your devices and their inter-connectivity. It is the basis of almost
all pyATS | Genie automation.

> YAML is designed to be a white-space sensitive, human-readable data
> representation/serialization language.

**A Very Simple Testbed YAML File**

```yaml
devices:                                # section describing your devices
    csr1000v-1:                             # device hostname -> used for matching prompt in Unicon
        type: router                        # switch | router
        os: iosxe                           # os -> used to determine Unicon connection plugin to load
        connections:                            # section describing all device connections
            console:                                # console connection block
                command: mock_device_cli --os iosxe --mock_data_dir recordings/yamls/csr --state execute
                protocol: telnet
                ip: 172.25.192.90
                port: 17001

```

> File copy available at [files/simple-testbed.yaml](files/simple-testbed.yaml).

To check whether your newly defined testbed YAML file is syntactically correct,
you can check its content using the `pyats validate testbed <file>` command.

```bash

pyats validate testbed files/simple-testbed.yaml
# Loading testbed file: files/simple-testbed.yaml
# --------------------------------------------------------------------------------
#
# Testbed Name:
#     simple-testbed
#
# Testbed Devices:
# .
# `-- csr1000v-1 [router/iosxe]
#
# Warning Messages
# ----------------
#  - Device 'csr1000v-1' missing 'platform' definition
#  - Device 'csr1000v-1' has no interface definitions
#
# YAML Lint Messages
# ------------------
```

Let's now load this testbed file in Python, and, like above, initiate 
connection to our device and do some fun stuff.

```python
from genie.testbed import load

# load the testbed file
testbed = load('files/simple-testbed.yaml')

# let's see our testbed devices
testbed.devices
# TopologyDict({'csr1000v-1': <Device csr1000v-1 at 0x10cd0a3c8>})

# get the device we are interested in
csr = testbed.devices['csr1000v-1']

# connect and run commands
csr.connect()
csr.execute('show interfaces')
```

Now let's expand our concept - throw in as bigger testbed yaml file.

```yaml
testbed:
    name: CL-DEVWKS-2808

devices:
    nx-osv-1:
        type: switch
        os: nos
        alias: uut
        credentials:
            default:
                username: admin
                password: cisco
            enable:
                password: cisco
        connections:
            console:
                command: mock_device_cli --os nxos --mock_data_dir recordings/yamls/nxos --state execute
                protocol: telnet
                ip: 172.25.192.90
                port: 9001
    
    csr1000v-1:
        type: router
        os: iosxe
        alias: helper
        credentials:
            default:
                username: admin
                password: cisco
            enable:
                password: cisco
        connections:
            console:
                command: mock_device_cli --os iosxe --mock_data_dir recordings/yamls/csr --state execute
                protocol: telnet
                ip: 172.25.192.90
                port: 9002
            mgmt:
                protocol: ssh
                ip: 10.1.3.50
               
```

We can now connect to each testbed device individually.

```python
from genie.testbed import load

# load the testbed file
testbed = load('files/complex-testbed.yaml')

# because we assigned aliases to each device, we can refer by alias instead
nx = testbed.devices['uut']
csr = testbed.devices['helper']

# connect and run commands
for device in [nx, csr]:
    device.connect(via = 'console')
    device.execute('show version')
```

Note that we are also specifying multiple connection pathways to our device. 
For example, in the CSR device, we've defined both the management VTY through 
ssh, and as well the standard console.

When there are multiple connection pathways, you specify which connection 
path to use, using `via`:

```python
# assuming you followed the above example and:
#   1. loaded the testbed
#   2. assigned csr device to 'csr' variable.

# connect to mgmt 
csr.connect(via = 'mgmt')
```

Testbed YAML `connections:` block is the entrypoint for defining the various
"mechanisms" of how to connect to your devices. It's a quite flexible mechanism,
where connectivity is described by both how (eg, protocol), and using what (eg,
the class/object to use to handle the connection). 

Internally in pyATS, this is implemented using what's called connection managers
and connection implementations. The default connection implementation, [Unicon](https://developer.cisco.com/docs/unicon), supports CLI connectivity (through SSH, telnet, proxy servers etc). Additional
mechanisms are also available, eg, [NETCONF/YANG](https://yangconnector.readthedocs.io/en/latest/index.html).

## Password Security

If you are uncomfortable with putting straight username and passwords in your 
testbed file, you can also use the credentials crypto feature, as documented
in the [topology credentials documentation](https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html#credential-password-modeling). Make sure to also read the 
[pyATS secret string guide](https://pubhub.devnetcloud.com/media/pyats/docs/utilities/secret_strings.html#)
and make your keys secure.

First, let's create our personal, private pyATS configuration file, and:

1. set it to use a cryptographic safe string encoder
2. ensure `cryptography` package is installed
3. generate our secret key
4. secure the configuration file
5. add our encrypted passwords to testbed YAML file.

```bash

# install cryptography
pip install cryptography

# create pyATS configuration directory
mkdir ~/.pyats/

# set it to use FernetSecretStringRepresenter
vim ~/.pyats/pyats.conf
# add the following:
# [secrets]
# string.representer = pyats.utils.secret_strings.FernetSecretStringRepresenter

# save, exit, now generate our safe key
pyats secret keygen
# output example:
# Newly generated key :
# DFSeRzYi_4Tp42QVzQd5AGiOo7_qAmtRJQ1wnViVYpk=

# edit ~/.pyats/pyats.conf and add the key in
# it should now look like this:
# [secrets]
# string.representer = pyats.utils.secret_strings.FernetSecretStringRepresenter
# string.key = DFSeRzYi_4Tp42QVzQd5AGiOo7_qAmtRJQ1wnViVYpk=

# save exit, now secure the file
chmod 600 ~/.pyats/pyats.conf

# generate your encrypted passwords
pyats secret encode cisco123
# Encoded string :
# gAAAAABeLF7bLzZMMtaAPcUO8VUdOt8v87llMpEoorgW-yL4wK5FLHqeU2wnyo3Hg8cysNaHPeQjuhhOGZKj98u2xbOg5y3_Mw==

# you can also decode a password from its encrypted form
pyats secret decode gAAAAABeLF7bLzZMMtaAPcUO8VUdOt8v87llMpEoorgW-yL4wK5FLHqeU2wnyo3Hg8cysNaHPeQjuhhOGZKj98u2xbOg5y3_Mw==
# Decoded string :
# cisco123
```
You can now use the newly generated encoded string in your testbed YAML file's
`credentials:` block, where a typical password string goes, put in instead:
`"%ENC{<encoded-string-here>}"`. Eg:

```yaml
devices:
    csr1000v-1:
        type: router
        os: iosxe
        alias: helper
        credentials:
            default:
                username: admin
                password: "%ENC{w6DDmsOUw6fDqsOOw5bDiQ==}"
        connections:
            mgmt:
                protocol: ssh
                ip: 10.1.3.50
```

> Note:
> 
>   By default if you don't use a cryptographically safe secret string method
>   (eg, without pyats.conf content), there is a built-in string "scrambler"
>   that gets used, but is much less safe.
> 
>   In addition, you should make an effort to not share the secret key with
>   other people. Treat it with the same respect as your SSH key, and/or your
>   house key.


Further reading on pyATS testbed file and connection details:
- support for credential prompts, encryptions: https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html#credential-password-modeling
- schema: supported testbed yaml keys https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html#
- how connection is modeled and controlled, including support for multiple 
  simultaneous connection to the same device https://pubhub.devnetcloud.com/media/pyats/docs/connections/manager.html#


## Step 2: Parsing Device Outputs

> For the remainder of this session, we'll be using the following pre-built
> testbed yaml file:
> 
>   `files/workshop-testbed.yaml`

Now that you have connectivity to your devices, let's do something more fun.

NetDevOps and automation is based on being able to programmatically make 
decisions on your network device states. To do that, we need to first "convert"
device output into something more "Pythonic" - using parsers.

pyATS | Genie comes with over 1500 parsers. You can access the list of all 
available parsers at https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/.

To use these parsers, first load your testbed yaml file.

```python
from genie.testbed import load

testbed = load('files/workshop-testbed.yaml')
uut = testbed.devices['uut']
uut.connect()
```

Wait wait wait - do I have to type this every single time? There must be a
better way!

```bash
# launch python interactive shell, and load the testbed yaml file
genie shell --testbed-file files/workshop-testbed.yaml
# Welcome to Genie Interactive Shell
# ==================================
# Python 3.6.5 (default, Jun 27 2018, 10:39:16)
# [GCC 4.2.1 Compatible Apple LLVM 10.0.0 (clang-1000.10.25.5)]

# >>> from genie.testbed import load
# >>> testbed = load('files/workshop-testbed.yaml')
# -------------------------------------------------------------------------------
# >>>
```

> Note:
>   
>   Note that starting v20.1 release, `genie shell` command will be merged into
>   the main pyATS command as part of a harmonization effort. The new command
>   will be `pyats shell` instead.

Now the testbed is loaded automatically for you, and available as the `testbed`
variable for you to use in this interactive shell.

Because we are using Genie, extending the core pyATS functionality, once we
connect to testbed devices, we can do... more!

```python
# get our device
uut = testbed.devices['uut']

# connect to it
uut.connect()

# leverage parsers - a Genie functionality!
# (note - make sure to use full commands)
uut.parse('show version')

# save it to variable
intfs = uut.parse('show interface')

```

This invokes the [show interface parser](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers/show%20interface). Remember that Genie libraries are open
source? You can view the source code [here](https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/nxos/show_interface.py#L150).

In the Genie parser library, all parsers return dictionaries. Each dictionary is 
described by its own schema, giving you an indication of what the parser will 
return. 

Following this schema, now let's check for our interface's information

```python
intfs.keys()

# reach into the structure and get something interesting
intfs['Ethernet2/1']['enabled']

import pprint
pprint.pprint(intfs['Ethernet2/1']['counters'])
```

Can you think of... the things you can do now, with this?

```python
# make sure interface has no CRC errors
for intf, intf_data in sorted(intfs.items()):
    if 'counters' in intf_data and 'in_crc_errors' in intf_data['counters']:
        print('%-20s' % intf, intf_data['counters']['in_crc_errors'])
    else:
        print('%-20s' % intf, '---')

```


## Step 3: Profile Device Features

What you have now is awesome. But we're still dealing with single CLIs. How can
we step back, get a bigger picture in view, and look at an entire feature?

While we ponder that, let's step back a bit. Even if we were just parsing
show commands, show commands are particular to each platform. Even for just
interfaces, you'll notice that

- for IOSXE, the command is `show interfaces`
- for NXOS, the command is `show interface`

This means our script above isn't portable...

[Genie models](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models/interface) to the rescue!

Genie models are YANG-inspired Python classes that implement a whole 
feature/protocol agnostically. They are called YANG-inspired because the 
development team studied the YANG models of various platforms and crafted 
their own. Why? Because YANG is a machine-to-machine descriptor, and NETCONF 
XML comes with its own angle bracket tax…

Built to be human-friendly and engineered to work across different platforms 
and OSes, Genie models enable users to interact with network devices/protocols
in a holistic, high-level and Pythonic fashion. 

```python

# get our device
uut = testbed.devices['uut']

# connect to it
uut.connect()

# let's learn a whole model instead
bgp = uut.learn('bgp')

# now let's look at what we learnt
import pprint
pprint.pprint(bgp.info)

# what if we could... track the number of neighbors we have?
num_nbr = 0

for bgp_instance in bgp.routes_per_peer['instance'].values():
    for vrf in bgp_instance['vrf'].values():
        for nbr in vrf['neighbor'].values():
            num_nbr += 1

print(num_nbr)
```

Because Genie models are agnostic across different platforms, you can write a 
piece of code once, and port it across different devices.


## Step 4: Putting It All Together To Python Script

Now let's put together everything we've learnt and write a useful Python script. 
For this script, we'll make it interesting and for each connected device, do the
following:

- display hostname
- display software version and hardware information
- print a table of all interfaces and their CRC error counter
- print the # of BGP neighbors they have

For this script, because we want to print a nice table, let's make use of an
awesome PyPI package called [tabulate](https://bitbucket.org/astanin/python-tabulate/src/master/)

```bash
# install tabulate as a dependency
pip install tabulate
```

```python
import os
HERE = os.path.dirname(__file__)

from tabulate import tabulate
from genie.testbed import load
    
if __name__ == '__main__':
    testbed = load(os.path.join(HERE, 'workshop-testbed.yaml'))

    uut = testbed.devices['uut']

    uut.connect()
    info = uut.learn('platform')
    bgp = uut.learn('bgp')

    # print useful information
    print('\n' + '-'*80)
    print('Hostname: %s' % uut.name)
    print('Software Version: %s %s\n' % (info.os, info.version))
    
    nbr_info = []
    for bgp_instance in bgp.routes_per_peer['instance']:
        for vrf in bgp.routes_per_peer['instance'][bgp_instance]['vrf']:
            for nbr in bgp.routes_per_peer['instance'][bgp_instance]['vrf'][vrf]['neighbor']:
                nbr_info.append((bgp_instance, vrf, nbr))
    
    print(tabulate(nbr_info, headers = ['BGP Instance', 'VRF', 'Neighbor']))

    print('\nTotal # of Active Neighbors: %s' % len(nbr_info))
    print('-'*80 + '\n')
```

## Step 5: pyATS Test Script, Logs & Etc

In the last section you've learnt about how to write straight forward Python 
scripts that leverages components of pyATS, and enable you as a Network 
Engineer to focus on building _"business logic"_ instead of fiddling with the 
details of programming, device interactions and parsing libraries.

But so far all that code goes into just simple scripts - and we rely on screen
printing (eg, `print()`) for message. For traceability, archiving and going
from simple if-else logic into testcases, we can leverage to full power of
a pyATS as a test framework..

First, let's convert the above Python script into pyATS testcases:

- we'll create a pyATS test script file
- break down the above script functionality into different parts of the test
  script
- run the script inside a pyATS *job*
- see the log archive.

To write a pyATS test script and corresponding testcases, create a `.py` file,
import `pyats.aetest` and define your sections. Inside any test script, your
"CommonSetup" sections runs first at the beginning (eg, to setup connectivity),
"Testcases" run in the order that they are defined, and "CommonCleaup" runs
at the end of the script.

See [testsuite/testscript.py](testsuite/testscript.py)

A pyATS test script be run both standalone (just like regular Python files), 
which does some nice result printing, but is much better when run under a job,
using `pyats run job` command.

Here's the content of our job file: [testsuite/job.py](testsuite/job.py)


This command takes care of:
- loading the testbed file and passing it in as the final object 
- creating archives, saving the environment information, logs
- generating result reports

and enables you to view the logs in browser.

Let's try it:

```bash
# run our job, and pass in the intended testbed YAML
pyats run job testsuite/job.py --testbed-file files/workshop-testbed.yaml
```

Everything we ran is now archived into log format in your user directory.
To view these logs, use the logs commands:

```bash
# list all logs so far
pyats logs list

# see the last log
pyats logs view
```

## Extras: Device Connection Under the Bonnet

Automation revolves around being able to programmatically establish connection
to your testbed devices. There are tools out there today that help you with
this, for example:

- [Paramiko](http://www.paramiko.org/): Python implementation of SSH client 
- [Pexpect](https://pexpect.readthedocs.io/en/stable/): Python module for 
  spawning child applications (e.g., telnet/ssh) and interacting with them 
- [Netmiko](https://github.com/ktbyers/netmiko): multi-vendor library that
  simplifies Paramiko SSH connections to network devices 

These libraries are good at establishing low-level connectivity to your devices,
and allow basic device interactions. However, what they do not provide is 
high-level services: stateful handling of various router/switch prompt states, 
and advanced mechanisms such as dialogs prompts, etc.

In the pyATS | Genie automation ecosystem, the de-facto device control library
is called [Unicon](https://developer.cisco.com/docs/unicon/).
In the workshop above, whenever we are establishing connectivity to our testbed
devices, we are using Unicon.

Compared to the solutions above, Unicon provides both low-level connectivity 
APIs, eg `sendline`, `expect`, but also high-level apis such as `execute`, 
`configure`, `ping`, etc., and the system dialogs for different platforms can be
automatically handled.

Testbed YAML gives you a more human way of describing testbed devices and simply
using them as objects, and establishing connectivity. But if you are interested
in what's going on under the hood, you can use Unicon directly in your Python 
code. 

Here are some neat functionalities w.r.t. Unicon:

- Automatically learn the hostname (within reason)
- Log connection interactions to a whole separate file
- Connection through proxies (jump hosts)
- RobotFramework support/keys

> The example below uses Cisco [DevNet Sandbox](https://developer.cisco.com/site/sandbox/)
> [IOSXE Always-ON testbed](https://devnetsandbox.cisco.com/RM/Diagram/Index/38ded1f0-16ce-43f2-8df5-43a40ebf752e?diagramType=Topology).

```python
# import connection implementation
from unicon import Connection

# create connection object instance
conn = Connection(hostname = 'csr1000v-1',
                  start = ['ssh developer@ios-xe-mgmt-latest.cisco.com -p 8181'],
                  line_password='C1sco12345',
                  os = 'iosxe')

# start the connection
conn.connect()

# now you can do stuff
conn.execute('show version')
conn.execute('show run | section interface')

# configure stuff
conn.configure('''
interface GigabitEthernet2
   ip address 1.1.1.1 255.255.255.0
   no shutdown
''')

conn.configure('''
interface GigabitEthernet2
   no ip address
   shutdown
''')

# ping an ip
conn.ping('10.10.20.48')

# traceroute an ip
conn.traceroute('10.10.20.48')

```

> Notice how the ping and traceroute interfaces are automatically handled for you.

What you have at hand is now a Unicon connection class instance. Each instance,
depending on the specified OS, supports various different services.

Under Unicon connection framework, the core handles boilerplate connection
details such as spawning child processes, send/receive/expect output, etc. Per
platform support is achieved through platform plugins. These plugins are 
open-source, and available on GitHub: https://github.com/CiscoTestAutomation/unicon.plugins

Each platform plugin contains information such as:

- expected command prompt for each state of the device (eg, enable, configure)
- various service implementations (eg, `reload()`)

There is no hard-coded information for Cisco-only platforms - everything is a
plugin. This means you can adjust the behavior for your target platform, or, 
implement your own platform plugin for other vendors.


## Wrapping It Up

In this workshop you've learned the basics of how to start programming with 
pyATS:

- defining your testbed YAML file
- connecting to device
- sending and receiving commands to and from your devices
- invoking parsers and models from pyATS/Genie library

Arms with the above, you should be able to start automating some aspects of your
day-to-day activies. Hopefully you had fun, and find this enjoyable!