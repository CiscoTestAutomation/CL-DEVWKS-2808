# DEVWKS-2808 Main Workshop Content

NetDevOps revolves around the concept of being able to automatically deploy, 
and more importantly, validate and verify your changes were successful, and that
the expected outcomes are seen.

In this workshop, we’ll dive deep into the world of Python programming with 
Cisco pyATS/Genie SDK: 

1. how to represent your testbed devices and its topology in YAML
2. connect to the devices
3. parse your device outputs
4. profile your device features
5. and build a full-on script!


## Step 1: Defining a Testbed YAML File

Automation revolves around being able to programmically establish connection
to your testbed devices. To do that, we need to first "describe" what devices
we have, and "how" to connect to them. In pyATS | Genie ecosystem, this is 
done using a testbed file. 

Testbed files leverages [YAML](https://yaml.org/spec/1.2/spec.html) syntax to
describes your devices and their inter-connectivity. It is the basis of almost
all pyATS | Genie based automation.

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

> Note - 
> 
> If you have real devices - you can put in their device information and
> connect to them. For the ease of this workshop, we provided mock devices.
> They're not real devices, but "emulate" what a device can do, using pure
> Python code.
>
> To use the mock device, do: `. env/testbed`.
> This sets the environment variables needed for the engine to "connect" to
> the provided mock devices.
>
> To unset the environment variables, do `. env/unset`

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

Now let's expand our concept - throw in a slightly bigger testbed yaml file.

```yaml
testbed:
    name: CLUS-19-DevWks-2808

devices:
    nx-osv-1:
        type: switch
        os: nos
        alias: 'uut'
        tacacs:
            login_prompt: "login:"
            password_prompt: "Password:"
            username: "admin"
        passwords:
            tacacs: Cisc0123
            enable: admin
            line: admin
        connections:
            console:
                protocol: telnet
                ip: "172.25.192.90"
                port: 17028
    
    csr1000v-1:
        type: router
        os: iosxe
        alias: helper
        tacacs:
            login_prompt: 'login:'
            password_prompt: 'Password:'
            username: cisco
        passwords:
            tacacs: cisco
            enable: cisco
            line: cisco
        connections:
            console:
              protocol: telnet
              ip: 172.25.192.90
              port: 17002
```

We can now connect to each testbed device individually.

```python
from genie.testbed import load

# load the testbed file
testbed = load('files/two-device-testbed.yaml')

# because we assigned aliases to each device, we can refer by alias instead
nx = testbed.devices['uut']
csr = testbed.devices['helper']

# connect and run commands
for device in [nx, csr]:
    device.connect()
    device.execute('show version')
```

It is possible to specify multiple methods of connecting to your devices. Eg:

```yaml

devices:
    csr1000v-1:
        type: router
        os: iosxe
        connections:
            console:
                protocol: telnet
                ip: 172.25.192.90
                port: 17001
            mgmt:
                protocol: ssh
                ip: 10.1.3.50
```

You can specify which connection desciption to use, as `via`:

```python
# assuming you followed the above example and:
#   1. loaded the testbed
#   2. assigned csr device to 'csr' variable.

# connect to mgmt 
csr.connect(via = 'mgmt')
```

If you are uncomfortable with putting straight username and passwords in your 
testbed file, you can use environment variables instead. 

```yaml
devices:
    csr1000v-1:
        type: router
        os: iosxe
        alias: helper
        tacacs:
            username: "%ENV{DEVICE_USERNAME}"
        passwords:
            tacacs: "%ENV{DEVICE_TACACS_PWD}"
            enable: "%ENV{DEVICE_ENABLE_PWD}"
            line: "%ENV{DEVICE_LINE_PWD}"
        connections:
            console:
              protocol: telnet
              ip: 172.25.192.90
              port: 17002
```
Ensure the corresponding environment variables are set - during testbed file
loading, these references will be then subsitituted with actual values.

Further reading on pyATS testbed file and connection details:
- schema: supported testbed yaml keys https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html#
- how connection is modeled and controlled, including support for multiple 
  simultaenous connection to the same device https://pubhub.devnetcloud.com/media/pyats/docs/connections/manager.html#

> Note:
>
> Under pyATS | Genie design, connection implementation exists in the form of
> a library. You can override the default connection class (Unicon) if you wish,
> and provide your own implementation.

## Mocked Testbed/Devices

For the remainder of this workshop, we'll be using the pre-created testbed mock
file:

```text
files/workshop-testbed.yaml
```

Mock devices are "pre-recorded" device interactions that can be "played back".
This eliminates the need to use real devices during a training session


## Step 2: Parsing Device Outputs

Now that you have connectivity to your devices, let's do something more fun.

NetDevOps and automation is based on being able to programmatically make 
decisions on your network device states. To do that, we need to first "convert"
device output into something more "Pythonic" - using parsers.

pyATS | Genie comes with over 1000 parsers. You can access the list of all 
available parsers at https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/parsers.

To use these parsers, first, load your testbed yaml file.

```python
from genie.testbed import load

testbed = load('files/workshop-testbed.yaml')
uut = testbed.devices['uut']
uut.connect()
```

Wait wait wait - do I have to type this every single time? There's must be a
better way!

```bash
# launch python interactive shell, and load teh testbed yaml file
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

Now the testbed is loaded automatically for you, and available as the `testbed`
variable for you to use in this interfactive shell

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

This invokes the [show interface parser](https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/parsers/show%20interface). Remember that Genie libraries are open
source? You can view the source code [here](https://github.com/CiscoTestAutomation/genieparser/blob/master/src/genie/libs/parser/nxos/show_interface.py#L145).

In Genie parser library, all parsers returns dictionaries. These return 
dictionaries are described by its own schema, giving you an indication of
what the parser will return. 

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

While we ponder about that, let's step back a bit. Even if we were just parsing
show commands - show commands are particular to each platform. Even for just
interfaces, you'll notice that

- for IOSXE, the command is `show interfaces`
- for NXOS, the command is `show interface`

This means our script above isn't portable...

[Genie models](https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models) to the rescue!

Genie models are YANG-inspired Python classes that implements a whole 
feature/protocol agnostically. They’re called YANG-inspired because the 
development team studies the YANG models of various platforms and crafted 
their own. Why? Because YANG is a machine-to-machine descriptor, and NETCONF 
XML comes with its own angle bracket tax…

Built to be human-friendly and engineered to works across different platforms 
and OSes, Genie models enables users to interact with network devices/protocols
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

for bgp_instance in bgp.info['instance'].values():
    for vrf in bgp_instance['vrf'].values():
        for nbr in vrf['neighbor'].values():
            if nbr['session_state'] =='established':
                num_nbr += 1
```

Because Genie models are agnostic across different platforms, you can write a 
piece of code once, and port it across different devices.


## Step 4: Putting It All Together

Now let's put everything we've learnt and write a useful script together. For
this script, we'll make it interesting and for each connected device, do the
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
    helper = testbed.devices['helper']

    uut.connect()
    info = uut.learn('platform')
    bgp = uut.learn('bgp')

    # print useful information
    print('\n' + '-'*80)
    print('Hostname: %s' % uut.name)
    print('Software Version: %s %s\n' % (info.os, info.version))
    
    nbr_info = []
    for bgp_instance in bgp.info['instance']:
        for vrf in bgp.info['instance'][bgp_instance]['vrf']:
            for nbr in bgp.info['instance'][bgp_instance]['vrf'][vrf]['neighbor']:
                state = bgp.info['instance'][bgp_instance]['vrf'][vrf]['neighbor'][nbr]['session_state']
                nbr_info.append((bgp_instance, vrf, nbr, state))
    
    print(tabulate(nbr_info, headers = ['BGP Instance', 'VRF', 'Neighbor', 'State']))

    active_nbr = len([i for i in nbr_info if i[-1].lower() == 'established'])
    print('\nTotal # of Active Neighbors: %s' % active_nbr)
    print('-'*80 + '\n')

```


## Extras: Device Connection Under the Bonnet

Automation revolves around being able to programmically establish connection
to your testbed devices. There are tools out there today that helps you with
this, eg:

- [Paramiko](http://www.paramiko.org/): Python implementation of SSH client 
- [Pexpect](https://pexpect.readthedocs.io/en/stable/): Python module for 
  spawning child applications (eg, telnet/ssh) and interact with them 
- [Netmiko](https://github.com/ktbyers/netmiko): multi-vendor library that
  simplifies Paramiko SSH connections to network devices 

These libraries are good at establishing low-level connectivity to your devices,
and allows basic device interactions. However, what they do not provide is 
high-level services: stateful handling of various router/switch prompt states, 
and advanced mechanisms such as dialogs prompts, etc.

In pyATS | Genie automation ecosystem, the de-facto device control library
is called [Unicon](https://pubhub.devnetcloud.com/media/pyats-packages/docs/unicon/index.html).
In the workshop above, whenever we are establishing connectivity to our testbed
devices, we are using Unicon.

Compared to the solutions above, Unicon provides both low-level connectivity 
APIs, eg `sendline`, `expect`, but also high-level apis such as `execute`, 
`configure`, `ping`, etc, the system dialogs for different platforms can be
automatically handled.

Testbed YAML gives you a more human way of describing testbed devices and simply
using them as objects, and establishing connectivity. But if you are interested
in what's going on under the hood, you can use Unicon directly in your Python 
code. 

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
Notice how the ping and traceroute interfaces are automatically handled for you.

What you have at hand is now a Unicon connection class instance. Each instance,
depending on the specified OS, supports various different services.

- Connection Documentation: https://pubhub.devnetcloud.com/media/pyats-packages/docs/unicon/user_guide/connection.html
- Supported Platforms: https://pubhub.devnetcloud.com/media/pyats-packages/docs/unicon/user_guide/introduction.html#supported-platforms
- Services per OS: https://pubhub.devnetcloud.com/media/pyats-packages/docs/unicon/user_guide/services/index.html

Under Unicon connection framework, the core handles boilerplate connection
details such as spawning child processes, send/receive/expect output, etc. Per
platform support is achieved through platform plugins, under:

```bash
    # note - * represents your python version.
    $VIRTUAL_ENV/lib/python*/site-packages/unicon/plugins/
```

Each platform plugin contains information such as:

- expected command prompt for each state of the device (eg, enable, configure)
- various service implementations (eg, `reload()`)

There is no hard-coded information for Cisco-only platforms - everything is a
plugin. This means you can adjust the behavior for your target platform, or, 
implement your own platform plugin for other vendors.

