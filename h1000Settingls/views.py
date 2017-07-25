from django.shortcuts import render
from django.http import HttpResponse,HttpResponseBadRequest
from django.http import  HttpResponseRedirect, HttpResponsePermanentRedirect
from django.views.decorators.csrf import csrf_exempt

from utils.cmdutils import execute_cmd
import os
import threading


# Create your views here.

def index(request):
    """

    :param request:
    :return:
    """
    return render(request, "index.html")

@csrf_exempt
def profile(request):
    """

    :param request:
    print request
    :return:
    """
    result = "H1000 setting is not OK,Cluster is not running..."
    status = -1
    msg = ""
    print request.POST
    node_number = int(request.POST.get("nodenumber", 0))
    vip = request.POST.get("vip", "")
    netmask = request.POST.get("nodenetmast", "")
    gateway = request.POST.get("nodegateway", "")
    dns = request.POST.get("nodedns", "")

    if not node_number:
        return HttpResponseBadRequest(HttpResponse('Please select valid node number!!!'))

    if not vip or not netmask or not gateway or not dns:
        return HttpResponseBadRequest(HttpResponse('Please input valid node network address info!!!'))

    try:
        status, msg = init_node_cluster_monitor()
        if status != 0:
            return HttpResponse(msg)

        status, msg = set_node_vip(vip=vip, netmask=netmask, gateway=gateway, dns=dns)
        if status != 0:
            return HttpResponse(msg)
        status, msg = set_node_ip(node_ip_info=request.POST, node_number=node_number, netmask=netmask, gateway=gateway, dns=dns)
        if status != 0:
            return HttpResponse(msg)
        status, msg = init_pxe_env(node_number=node_number)
        if status != 0:
            return HttpResponse(msg)
        try:
            monitor = Monitor(threadName="nodeMonitor", vip=vip)
            monitor.start()
        except Exception as e:
            return HttpResponse(e.message)

        return HttpResponsePermanentRedirect("/status/")
    except Exception as e:
        result = e.message

    return HttpResponse(result)


def status(request):
    """

    :param request:
    :return:
    """
    result = ""
    cmd = "tail -n 100 /root/status.txt"
    print cmd
    result, msg = execute_cmd(cmd=cmd)
    return render(request, "status.html", {"string": msg})


class Monitor(threading.Thread):
    def __init__(self, threadName, vip=""):
        super(Monitor, self).__init__(name=threadName)
        self.vip = vip

    def run(self):
        """

        :return:
        """
        status, msg = run_cluster_monitor(vip=self.vip)


def set_node_vip(vip="", netmask="", gateway="", dns=""):
    """

    :param vip:
    :param netmask:
    :param gateway:
    :param dns:
    :return:
    """
    if not vip:
        return -1, "vip is invalid."

    vip_file_path = "/opt/cluster_service/network/node_vip_info.txt"

    with open(vip_file_path, mode='w') as fvip:
        content = "vip {0} {1} {2} {3}\n".format(vip, netmask, gateway, dns)
        fvip.write(content)

    return 0, "Node vip set ok."


def init_node_cluster_monitor():
    """

    :return:
    """
    cmdfile = "/opt/cluster_service/init_cluster_monitor_env.sh"
    if not os.path.exists(cmdfile):
        return -1, "cluster monitor sh is not exist."

    status, msg = execute_cmd(cmd="bash "+cmdfile)

    return status, msg


def init_pxe_env(node_number=0):
    """

    :return:
    """
    cmdfile = "/opt/cluster_service/init_pxe_env.sh"
    if not os.path.exists(cmdfile):
        return -1, "pxe env sh is not exist."
    cmd = cmdfile + " {0}".format(node_number)
    status, msg = execute_cmd(cmd="bash "+cmd)
    print cmd
    return status, msg


def set_node_ip(node_ip_info=None, node_number=0, netmask="", gateway="", dns=""):
    """

    :param node_ip_info:
    :param node_number:
    :return:
    """

    ip_file_path = "/opt/cluster_service/network/node_ip_info.txt"

    if not isinstance(node_ip_info, dict):
        return -1, "Node ip info is invlaid"

    with open(ip_file_path, mode="w") as fnodeip:
        for nodex in xrange(node_number):
            cur_node_ip = node_ip_info.get("nodename"+str(nodex+1), None)
            if not cur_node_ip:
                return -1, "cur node${0} ip is invalid.".format(nodex+1)
            content = "node{0} {1} {2} {3} {4}\n".format(nodex+1, cur_node_ip, netmask, gateway, dns)
            fnodeip.write(content)

    return 0, "Node ip conf ok."


def run_cluster_monitor(vip=""):
    """

    :return:
    """
    if not vip:
        return -1, "cluster monitor need a pub ip."

    cmdfile = "/opt/cluster_service/cluster_monitor.sh"
    if not os.path.exists(cmdfile):
        return -1, "cluster_monitor sh is not exist."
    cmd = cmdfile + " {0}".format(vip)
    cmd += ">>/root/status.txt"
    print cmd
    status, msg = execute_cmd(cmd="bash "+cmd)

    return status, msg
