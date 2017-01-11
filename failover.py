#! /usr/bin/python3

import time
import datetime
from netmiko import ConnectHandler
# start = datetime.datetime.now()

# NOTE: The IP ranges in this are for LAB purposes only.
# They are reserved ranges as documented in RFC5737:
# 203.0.113.0/24 (TEST-NET-3)

# TODO: Add latency test, slack integration

# below we add connection info
cisco_isr = {
    'device_type': 'cisco_ios',
    'ip':   '203.0.113.102',
    'username': 'python',
    'password': 'monty', }

net_connect = ConnectHandler(**cisco_isr)

# setting our condition variables to be checked:
ping_result = net_connect.send_command('ping 203.0.113.97 so g0/0')
check_route = net_connect.send_command('show run | s route')

# config commands we will send to the router
rm_route = ['no ip route 0.0.0.0 0.0.0.0 203.0.113.97']
add_route = ['ip route 0.0.0.0 0.0.0.0 203.0.113.97']

# set timestamp
ts = datetime.datetime.fromtimestamp(time.time()).strftime('\
[%Y-%m-%d] %H:%M:%S')


def main():
    ld = link_down()
    rp = route_present()

    # print('**DEBUG** ld: ' + ld + ' -- rp: ' + rp)
    if ld == 'y' and rp == 'y':
        # This will remove the primary static route
        net_connect.send_config_set(rm_route)

        # Write to log with timestamp
        log = open('/var/log/failover.log', 'a')
        log.write(ts + ': Failing over to secondary link g0/1 \n')
        log.close()

    elif ld == 'n' and rp == 'n':
        # This will re-add the primary static route
        net_connect.send_config_set(add_route)

        # Write to log with timestamp
        log = open('/var/log/failover.log', 'a')
        log.write(ts + ': Failing back to primary link g0/0 \n')
        log.close()

    else:
        return


def link_down():
    if '.....' in ping_result:
        return 'y'

    else:
        return 'n'


def route_present():
    if '203.0.113.97' in check_route:
        return 'y'

    else:
        return 'n'


if __name__ == '__main__':
    main()

# end = datetime.datetime.now()
# print('**DEBUG*** Time to complete:  ' + str(end - start))
