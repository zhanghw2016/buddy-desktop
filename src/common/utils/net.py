'''
Created on 2012-5-6

@author: yunify
'''

import os
import netaddr
import subprocess, re
from log.logger import logger
from constants import (
    SERVER_TYPE_VDI_SERVER, 
    VDI_SERVICE_PORT, 
    SERVER_TYPE_SERVER_PROXY, 
    SERVER_TYPE_AGENT_SERVER,
    SERVER_TYPE_DISPATCH_SERVER,
    SERVER_TYPE_PUSH_SERVER,
    VDI_AGENT_SERVICE_PORT,
    SERVER_TYPE_VDI_SCHEDULER_SERVER,
    VDI_SCHEDULER_SERVER_PORT,
    DISPATCH_SERVER_PORT,
    PUSH_SERVER_PORT,
    SERVER_TYPE_VDI_VDHOST_SERVER,
    VDI_VDHOST_SERVER_PORT,
    SERVER_TYPE_VDI_TERMINAL_SERVER,
    VDI_TERMINAL_SERVER_PORT,
    LOCALHOST
)

from utils.misc import exec_cmd, read_file
from constants import NETWORK_MARK
import socket
import struct
import fcntl
from netaddr.ip import IPAddress, IPNetwork

g_local_host_name = None
def get_hostname():
    ''' a simple code to get host name '''
    global g_local_host_name
    if g_local_host_name != None:
        return g_local_host_name
    
    if os.path.exists("/etc/hostname"):
        host_name = read_file("/etc/hostname")
        host_name = host_name.strip()
        if host_name:
            g_local_host_name = host_name
            return g_local_host_name
        
    g_local_host_name = socket.gethostname()
    return g_local_host_name

def get_hostname_by_ip(ip_addr):

    try:
        socket.setdefaulttimeout(3)
        names = socket.gethostbyaddr(ip_addr)
        for _name in names:

            if isinstance(_name, str):
                name = _name
            elif isinstance(_name, list):
                if not list:
                    continue
                name = _name[0]
            if is_valid_ip(name):
                continue
            idx = name.find(".")
            if idx > 0:
                return name[:idx]
            else:
                return name
    except:
        logger.critical("get hostname of [%s] failed" % (ip_addr))

    return None

def get_host_ip(hostname, suppress_warning=False):
    ''' get ip address of a host '''
    try:
        socket.setdefaulttimeout(3)
        ip = socket.gethostbyname(hostname)
    except:
        if suppress_warning:
            logger.error("get ip of [%s] failed" % (hostname))
        else:
            logger.critical("get ip of [%s] failed" % (hostname))

        # NOTE: can't return None, because in many cases, None means local host
        return hostname
    return ip

def is_reachable(remote_ip, retries=10):
    retries = retries
    while retries > 0:
        ret = exec_cmd("ping -c 1 -w 1 %s" % remote_ip)
        if ret != None and ret[0] == 0:
            return True
        retries -= 1

    return False

def get_ipv4_address():
    """ Returns IP address(es) of current machine """
    p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
    ifc_resp = p.communicate()
    patt = re.compile(r'inet\s*\w*\S*:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    resp = patt.findall(ifc_resp[0])
    return resp

g_local_mgmt_ip = ""
def get_local_mgmt_ip():
    """ Returns IP address of local mgmt ip """
    global g_local_mgmt_ip
    if g_local_mgmt_ip != "":
        return g_local_mgmt_ip
    full_host = "%s.mgmt.pitrix.yunify.com" % get_hostname()
    g_local_mgmt_ip = get_host_ip(full_host)
    return g_local_mgmt_ip

def get_mgmt_net_ip(host, suppress_warning=False):
    ''' get management network ip address '''
    if host == get_hostname():
        return get_local_mgmt_ip()
    full_host = "%s.mgmt.pitrix.yunify.com" % host
    return get_host_ip(full_host, suppress_warning=suppress_warning)

def try_get_mgmt_net_ip(hostname):
    ''' get mgmt_net ip address of a host '''
    if hostname == get_hostname():
        return get_local_mgmt_ip()
    
    try:
        suffix = ".mgmt.pitrix.yunify.com"
        fullhost = hostname if str(hostname).endswith(suffix) else \
            "%s%s" % (hostname, suffix)
        socket.setdefaulttimeout(3)
        ip = socket.gethostbyname(fullhost)
    except:
        logger.error("get ip of [%s] failed" % (hostname))
        return None
    return ip

def is_local_server(server):
    local_mgmt_ip = get_local_mgmt_ip()
    server_mgmt_ip = get_mgmt_net_ip(server)

    return local_mgmt_ip.strip() == server_mgmt_ip.strip()


g_local_user_ip = ""
def get_local_user_ip():
    """ Returns IP address of local user ip """
    global g_local_user_ip
    if g_local_user_ip != "":
        return g_local_user_ip
    full_host = "%s.user.pitrix.yunify.com" % get_hostname()
    g_local_user_ip = get_host_ip(full_host)
    return g_local_user_ip

def get_local_user_network():
    '''
    @return network in cidr format of user interface
    '''
    user_ip = get_local_user_ip()
    dev = get_local_user_dev()
    if not user_ip or not dev:
        return None

    ret = exec_cmd("ip a show dev %s|grep 'inet '|grep %s/|awk '{print $2}'|cut -d '/' -f 2"
                   % (dev, user_ip))
    if not ret or ret[0] != 0 or not ret[1] :
        logger.error("fail to find network for [%s] in [%s]"
                     % (user_ip, dev))
        return None

    mask = ret[1]

    net = IPNetwork("%s/%s" % (user_ip, mask))
    return str(net.cidr)

g_local_user_dev = ""
def get_local_user_dev():
    """ Returns device of local user network """
    global g_local_user_dev
    if g_local_user_dev != "":
        return g_local_user_dev

    user_ip = get_local_user_ip()
    ret = exec_cmd("ifconfig | grep -B 1 'inet addr:%s ' | grep HWaddr | awk '{print $1}'" % user_ip)
    if ret == None or ret[1] == "":
        logger.critical("get local user dev failed")
        return None
    g_local_user_dev = ret[1]
    return g_local_user_dev

def get_user_net_ip(host):
    ''' get user network ip address '''
    if host == get_hostname():
        return get_local_user_ip()
    full_host = "%s.user.pitrix.yunify.com" % host
    return get_host_ip(full_host)


def get_dev_by_ip(ip):
    ''' get interface name of an ip address '''

    for dev in os.listdir("/sys/class/net"):
        if dev in [".", "..", "lo"]:
            continue

        # don't check virtual nic and bridge
        if len(dev) == 8 and re.match(r'[0-9a-f]{8}', dev, re.M):
            continue

        ret = exec_cmd("ip addr show %s | grep 'inet %s/'" % (dev, ip), suppress_warning=True)
        if ret != None and ret[1] != "":
            return dev

    return None

def get_local_routing():
    ''' return [(network, dev, gw), ...]'''
    routing = []
    ret = exec_cmd("ip route list | grep 'scope link' | awk '{print $1, $3, $NF}'")
    if ret == None or ret[0] != 0:
        return routing
    for line in ret[1].splitlines():
        parts = line.split(" ")
        if len(parts) != 3:
            continue
        if not is_valid_ip(parts[2]):
            continue
        routing.append((parts[0], parts[1], parts[2]))
    return routing

def get_listening_url(server_type, port=None, listen_ip=None):
    '''
        get listening url
        Note: if this service listens to connection from outside, it must bound to mgmt ip for safety
    '''
    mgmt_ip = listen_ip
    if not mgmt_ip:
        mgmt_ip = LOCALHOST
        if not mgmt_ip:
            return None
    if server_type == SERVER_TYPE_VDI_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else VDI_SERVICE_PORT)
    elif server_type == SERVER_TYPE_SERVER_PROXY:
        if not port:
            return None
        return "tcp://%s:%d" % (mgmt_ip, port)
    elif server_type == SERVER_TYPE_AGENT_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else VDI_AGENT_SERVICE_PORT)
    elif server_type == SERVER_TYPE_VDI_SCHEDULER_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else VDI_SCHEDULER_SERVER_PORT)
    elif server_type == SERVER_TYPE_DISPATCH_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else DISPATCH_SERVER_PORT)
    elif server_type == SERVER_TYPE_PUSH_SERVER:
        return "tcp://%s:%d" % (listen_ip if listen_ip else "127.0.0.1", port if port else PUSH_SERVER_PORT)
    elif server_type == SERVER_TYPE_VDI_VDHOST_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else VDI_VDHOST_SERVER_PORT)
    elif server_type == SERVER_TYPE_VDI_TERMINAL_SERVER:
        return "tcp://127.0.0.1:%d" % (port if port else VDI_TERMINAL_SERVER_PORT)
    else:
        return None

def compare_ip(ip0, ip1):
    try:
        _ip0 = netaddr.IPAddress(ip0)
        _ip1 = netaddr.IPAddress(ip1)
        if _ip0 > _ip1:
            return 1
        if _ip0 < _ip1:
            return -1
        return 0
    except Exception, e:
        logger.error("invalid ip [%s] [%s]: %s", ip0, ip1, e)
        return -2

def ip_to_network(ip, netmask=NETWORK_MARK):
    try:
        cidr = IPNetwork("%s/%s" % (ip, netmask))
        return cidr.network
    except Exception, e:
        logger.error("invalid ip [%s]: %s", ip, e)
        return False

def network_inc(network, num):
    try:
        cidr = IPNetwork("%s" % network)
        return cidr.__iadd__(num)
    except Exception, e:
        logger.error("inc network[%s] fail: %s", network, e)
        return False

def network_to_network(network):
    try:
        cidr = IPNetwork("%s" % (network))
        return cidr.network
    except Exception, e:
        logger.error("invalid network [%s]: %s", network, e)
        return False    

def ip_in_network(ip, network):
    try:
        if isinstance(network, (list, tuple)) and len(network) == 2:
            is_in = netaddr.IPAddress(ip) in netaddr.IPRange(network[0], network[1])
        else:
            is_in = netaddr.IPAddress(ip) in netaddr.IPNetwork(network)
        if not is_in:
            return False
        return True
    except Exception, e:
        logger.error("invalid ip [%s]: %s", ip, e)
        return False

def network_in_network(ip_network, network):
    try:
        if isinstance(network, (list, tuple)) and len(network) == 2:
            is_in = netaddr.IPNetwork(ip_network) in netaddr.IPRange(network[0], network[1])
        else:
            is_in = netaddr.IPNetwork(ip_network) in netaddr.IPNetwork(network)
        if not is_in:
            return False
        return True
    except Exception, e:
        logger.error("invalid ip network [%s]: %s", ip_network, e)
        return False

def get_network_ips(network):
    ''' return ip list in this network '''
    try:
        # ip_network should not contain unicode
        network = str(network)
        ip_network = netaddr.IPNetwork(network)
        return list(ip_network)
    except Exception, e:
        logger.error("invalid network [%s]: %s", network, e)
        return None

def get_ip_range(start, end, excluded = []):
    ''' return ip list in this network '''
    
    if not start or not end:
        return None
    
    if excluded and not isinstance(excluded, list):
        excluded = [excluded]
    
    try:
        # ip_network should not contain unicode
        ip_list = list(netaddr.IPRange(start, end))
        ip_range = []
        for ip in ip_list:
            ip_range.append(str(ip))

        if len(excluded) > 0:
            for ip in excluded:
                if ip in ip_range:
                    ip_range.remove(ip)
        return ip_range
    except Exception, e:
        logger.error("invalid ipaddr range [%s-%s]: %s", start, end, e)
        return None    

max_vxnet_count = 200
def get_next_network(network, excluded = []):
    ''' return ip list in this network '''
    try:
        for _ in range(max_vxnet_count):
            network = str(network)
            ip_network = netaddr.IPNetwork(network)
            if str(ip_network) not in excluded:
                return str(ip_network)
            ip_network = ip_network.next()
            return None

    except Exception, e:
        logger.error("invalid network [%s]: %s", network, e)
        return None

def get_ip_network(network):
    ''' return IPNetwork '''
    try:
        ip_network = netaddr.IPNetwork(network)
        return ip_network
    except Exception, e:
        logger.error("invalid network [%s]: %s", network, e)
        return None

def get_norm_network(network):
    # normalize it
    n = get_ip_network(network)
    if not n:
        return None
    return "%s" % n.cidr

def get_norm_ip(ip):
    n = get_ip_network(ip)
    if not n:
        return None
    return str(n.ip)

def is_port_open(host, port):
    if not os.path.exists("/bin/nc"):
        return False
    ret = exec_cmd("/bin/nc -z -w 1 %s %s" % (host, port))
    if ret != None and ret[0] == 0:
        return True
    return False

def is_radius_port_open(host, port):
    if not os.path.exists("/bin/nc"):
        return False
    ret = exec_cmd("/bin/nc -vuz %s %s" % (host, port))
    if ret != None and ret[0] == 0:
        if len(ret)==3 and "radius" in ret[2]:
            return True
    return False

def is_valid_mac(mac_addr):
    ''' check if mac addr is valid
        @param mac_addr: mac address in string format like "52:54:77:8d:06:34"
    '''
    try:
        if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_addr.lower()):
            return True
    except:
        return False
    return False

def is_valid_ip(ip_addr):
    ''' check if ip address is valid
        @param ip_addr: ip address in string format like "127.0.0.1"
    '''
    try:
        netaddr.IPAddress(ip_addr, flags=1)
    except:
        return False
    return True

def get_valid_ip(ip_addr):
    ''' check if ip address is valid
        @param ip_addr: ip address in string format like "127.0.0.1"
    '''
    try:
        return netaddr.IPAddress(ip_addr, flags=1)
    except Exception, e:
        logger.error("invalid ip address [%s]: %s", ip_addr, e)
        return None

def is_valid_network(ip_network):
    ''' check if ip network is valid
        @param ip_addr: ip network in string format like "192.168.100.0/24"
    '''
    try:
        # ip_network should not contain unicode
        ip_network = str(ip_network)
        netaddr.IPNetwork(ip_network, flags=1)
    except:
        return False
    return True

def is_valid_host(host, max_length=63, max_label_length=63):
    ''' check if host is valid '''
    try:
        if len(host) == 0 or len(host) > max_length:
            return False
        labels = host.split(".")
        for label in labels:
            if not is_valid_domain_label(label, max_label_length=max_label_length):
                return False
        return True
    except:
        return False

def is_valid_domain_label(label, max_label_length=63):
    ''' check if domain label is valid '''
    try:
        if not re.match(r'^[a-zA-Z\d-]{1,%s}$' % max_label_length, label):
            return False
        if label[0] == '-' or label[-1] == '-':
            return False
        return True
    except:
        return False

def is_valid_ip_port(addr):
    '''check if it is ip:port format
    '''

    try:
        if not re.match(r"^(([1-9]?\d|1\d\d|25[0-5]|2[0-4]\d)\.){3}([1-9]?\d|1\d\d|25[0-5]|2[0-4]\d):\d{1,5}$", addr):
            return False
        return True
    except:
        return False

def get_ip_address(ifname):
    ''' get ip address from interface, eg: eth0 '''

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def is_local_ip_addr(ip_addr):
    ret = exec_cmd('ip addr show | grep "inet %s/"' % (ip_addr),
                   suppress_warning=True)
    if ret and ret[0] == 0:
        return True

    return False

def allocate_id(current_ids, min_id, max_id):
    """ allocate an id that fix into current ids

    @param current_ids: list of int
    @param min_id: min value of id (included)
    @param max_id: max value of id (included)
    @return: id allocated. None for fail
    """
    if max_id <= min_id:
        logger.error("max %s should be greater than mix %s" % (max_id, min_id))
        return None

    # filter invalid values
    if current_ids:
        current_ids = [i for i in current_ids if i >= min_id and i <= max_id]

    if not current_ids:
        return min_id

    if type(current_ids) is not list \
        and type(current_ids) is not tuple :
        logger.error("current_ids %s is not a supported type in _allocate_id"
                     % type(current_ids))
        return None

    current_ids.sort()
    allocated = None

    if current_ids[0] > min_id:
        return min_id

    if not allocated and len(current_ids) > 1:
        for i in range(len(current_ids) - 1):
            if current_ids[i + 1] - current_ids[i] > 1:
                allocated = current_ids[i] + 1
                break

    if not allocated:
        allocated = current_ids[-1] + 1

    if allocated > max_id:
        logger.error("max id reached in %s"
                     % (current_ids))
        return None
    return allocated

def allocate_ip(current_ips_str, network):
    """ allocate an ip from network

    @param current_ips_str: list of allocated ip address in string
    @param network: IPNetwork instance for ip to allocate
    @return: id allocated. None for fail
    """
    current_values = [IPAddress(i).value for i in current_ips_str if i]
    value = allocate_id(current_values, network[1].value, network[-2].value)
    return str(IPAddress(value)) if value else None

def allocate_ip_range(current_ips_str, start_ip, end_ip):
    """ allocate an ip from network

    @param current_ips_str: list of allocated ip address in string
    @param network: IPNetwork instance for ip to allocate
    @return: id allocated. None for fail
    """
    current_values = [IPAddress(i).value for i in current_ips_str if i]
    start_ip_value = IPAddress(start_ip).value
    end_ip_value = IPAddress(end_ip).value
    value = allocate_id(current_values, start_ip_value, end_ip_value)
    return str(IPAddress(value)) if value else None

def get_mac_addr(dev_name, ns_name=None):

    cmd = "ip link show dev %s|grep 'link/ether'|awk '{print $2}'" % dev_name
    if ns_name:
        cmd = "ip netns exec %s " % ns_name + cmd

    ret = exec_cmd(cmd, timeout=5, suppress_warning=True)
    if ret != None and ret[1] != "":
        mac_addr = ret[1]
        if is_valid_mac(mac_addr):
            return mac_addr

    return None

def get_bridge_ports(br_name):
    ''' get all ports of a bridge '''

    ports = []
    ret = exec_cmd("brctl show %s | grep -v 'interfaces' | awk '{print $NF}'" % (br_name))
    if ret != None and ret[1] != "":
        for port in ret[1].splitlines():
            if port != br_name and os.path.exists("/sys/class/net/%s" % port):
                ports.append(port)

    return ports

def get_last_subnet(network, subfix=24):

    vpc_network = netaddr.IPNetwork(network)
    # get the last subnet
    subnet = None
    for subnet in vpc_network.subnet(subfix):
        pass
    return subnet

def get_network_head_ip(network):
    n = get_ip_network(network)
    if not n:
        raise Exception("invalid network: [%s]" % network)
    return str(n[1])

def get_network_last_ip(network):
    n = get_ip_network(network)
    if not n:
        raise Exception("invalid network: [%s]" % network)
    return str(n[-2])

def get_network_prefixlen(network):
    n = get_ip_network(network)
    if not n:
        raise Exception("invalid network: [%s]" % network)
    return n.prefixlen

def get_sysctl(key, default=None):
    ret = exec_cmd("/sbin/sysctl -n %s" % key)
    if ret != None and ret[0] == 0:
        return ret[1].strip()
    return default

def get_vm_devs():
    ret = exec_cmd("ip link|grep -E ': [0123456789abcdef]{8}: '|awk '{print $2}'|cut -d ':' -f 1")
    if ret and ret[0] == 0 and ret[1]:
        return ret[1].splitlines()
    return []

def netdev_exist(devname):

    return os.path.exists("/sys/class/net/%s" % devname)

def iprange_to_cidrs(start_ip, end_ip):
    try:
        return netaddr.iprange_to_cidrs(start_ip, end_ip)
    except Exception, e:
        logger.error("invalid iprange [%s, %s]: %s", start_ip, end_ip, e)
    return None

def cidr_merge(ip_list):
    try:
        return netaddr.cidr_merge(ip_list)
    except Exception, e:
        logger.error("invalid ip list [%s]: %s", ip_list, e)
    return None

def check_route(route_info, destionation_network, router_ip, is_windows):
    """
    check route(destionation_network, router_ip) exist in route_info or not
    @param route_info: list of route
    @param destionation_network: network
    @param router_ip: ip
    @return: True if route exists
    """
    if not route_info:
        return False

    network_obj = IPNetwork(destionation_network)
    if is_windows:
        network = str(network_obj.network)
        netmask = str(network_obj.netmask)
        pattern = '.*%s.*%s.*%s.*' % (network, netmask, router_ip)
    else:
        network = str(network_obj)
        if network == '0.0.0.0/0':
            network = 'default'
        pattern = '.*%s.*%s.*' % (network, router_ip)

    for route in route_info:
        match = re.search(pattern, route)
        if match:
            return True
    return False


def combine_ip_addr(ip_net, addr):

    if not addr or not ip_net or not isinstance(addr, str):
        return None

    if not addr.startswith("."):
        return None

    prefixlen = get_network_prefixlen(ip_net)
    # only /24 network is supported
    if prefixlen != 24:
        return None

    _first_ip = get_network_head_ip(ip_net)
    _ip_addr = _first_ip[:-2] + str(addr)
    if is_valid_ip(_ip_addr) and ip_in_network(_ip_addr, ip_net):
        return _ip_addr

    logger.error("invalid configuration to combine addr [%s] and [%s]"
                 % (ip_net, addr))
    return None
