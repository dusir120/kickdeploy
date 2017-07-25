import  os
import sys
import commands


def execute_cmd(cmd=""):
    """

    :param cmd:
    :return:
    """
    try:
        result = commands.getstatusoutput(cmd)
    except Exception as e:
        print e.message

    return result[0], result[1]
