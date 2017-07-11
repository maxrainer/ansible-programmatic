'''
Created on 05.07.2017

@author: max
'''
import threading
import logging
from ansible.utils.display import Display
from ansible.errors import AnsibleParserError, AnsibleOptionsError

logger = logging.getLogger('transport')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.formatter = logging.Formatter('%(name)s - %(message)s')
logger.addHandler(handler)

class LogForward(Display):
    """
    Quick hack of a log forwarder
    """
 
    def display(self, msg, screen_only=None, *args, **kwargs):
        """
        Pass display data to the logger.
        :param msg: The message to log.
        :type msg: str
        :param args: All other non-keyword arguments.
        :type args: list
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        """
        # Ignore if it is screen only output
        if screen_only:
            return
        logging.getLogger('transport').info(msg)
 
    # Forward it all to display
    info = display
    warning = display
    error = display
    # Ignore debug
    debug = lambda s, *a, **k: True

class JobCLIAnsible(threading.Thread):


    def __init__(self, playbook, hosts, args=[]):
        if isinstance(hosts, basestring):
            self.hosts = hosts + ','
        elif hasattr(hosts, '__iter__'):
            self.hosts = ','.join(hosts) + ','
        else:
            raise AnsibleParserError('Can not parse hosts of type {}'.format(
            type(hosts)))
        