from django.shortcuts import render
from django.http import HttpResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt


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
    print request.POST
    node_number=request.POST.get("nodenumber",0)
    vip=request.POST.get("vip","")

    if not node_number:
        return HttpResponseBadRequest(HttpResponse('Please select valid node number!!!'))

    for nodex in xrange(int(node_number)):
        print request.POST.get("nodename"+str(nodex+1),"")

    return HttpResponse(2)