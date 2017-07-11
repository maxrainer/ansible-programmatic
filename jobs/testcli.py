'''
Created on 05.07.2017

@author: max
'''
from ansible.cli.playbook import PlaybookCLI
import os
from ansible.errors import AnsibleParserError, AnsibleOptionsError
from ansible.utils.display import Display
import logging

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
    
display = LogForward()

def execute_playbook(playbook, hosts, args=[]):
    """
    :param playbook: Full path to the playbook to execute.
    :type playbook: str
    :param hosts: A host or hosts to target the playbook against.
    :type hosts: str, list, or tuple
    :param args: Other arguments to pass to the run.
    :type args: list
    :returns: The TaskQueueHandler for the run.
    :rtype: ansible.executor.task_queue_manager.TaskQueueManager.
    """
    # Set hosts args up right for the ansible parser. It likes to have trailing ,'s
    if isinstance(hosts, basestring):
        hosts = hosts + ','
    elif hasattr(hosts, '__iter__'):
        hosts = ','.join(hosts) + ','
    else:
        raise AnsibleParserError('Can not parse hosts of type {}'.format(
            type(hosts)))
 
    # Create the cli object
    cli_args = ['playbook'] + args + ['-i', hosts, os.path.realpath(playbook)]
    logger.info('Executing: {}'.format(' '.join(cli_args)))
    cli = PlaybookCLI(cli_args)
    
    # Parse args and run it
    try:
        cli.parse()
        # Return the result:
        # 0: Success
        # 1: "Error"
        # 2: Host failed
        # 3: Unreachable
        # 4: Parser Error
        # 5: Options error
        result = cli.run()
        i = cli.options.inventory
        return result
    except (AnsibleParserError, AnsibleOptionsError) as error:
        logger.error('{}: {}'.format(type(error), error))
        raise error

if __name__ == '__main__':
    result = execute_playbook('/Users/max/Documents/dev/ansible/dev/site.yaml', ['ise'], ['-v'])
    print "s"


