'''
Created on 11.07.2017

@author: max
'''
from ansible.cli.playbook import PlaybookCLI

import os
import stat

from ansible.cli import CLI
from ansible.errors import AnsibleError
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.block import Block
from ansible.playbook.play_context import PlayContext
from ansible.utils.vars import load_extra_vars
from ansible.utils.vars import load_options_vars
from ansible.vars import VariableManager
from config.configuration import Configuration
from threading import Thread

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class PlaybookAPI(PlaybookCLI, Thread):
    
    def __init__(self, playbook, inventoryContainer, apijob):
        self.apijob = apijob
        playbook = Configuration.playbook_dir + '/' + playbook
        self.inventoryContainer = inventoryContainer
        super(PlaybookAPI, self).__init__(args=['playbook'] + [playbook], callback=None)
        Thread.__init__(self)
    
    def parse(self):
               
        parser = super(PlaybookAPI, self).base_parser(usage="API", inventory_opts=True)     
        self.parser = parser
        super(PlaybookAPI, self).parse()
        self.options.inventory = str(self.inventoryContainer.allHosts())
        self.options.listtasks = None
        self.options.listtags = None
        self.options.syntax = None
        self.options.module_path = None
        self.options.forks = 5
        self.options.become = False
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'
        self.options.diff = False
        self.options.check = False
        self.options.tags = ["all"]
        self.options.skip_tags = []
        self.options.extra_vars = [{'uuid':str(self.apijob.uuid), 'elastic_url':Configuration.elastic_url}]
#        self.options.extra_vars = []
        self.options.force_handlers = False
        self.options.start_at_task = None
        self.options.step = None
        self.options.subset = None
        self.options.verbosity = 3
        self.options.timeout = 5  

    def run(self):
        
        sshpass    = None
        becomepass    = None
        b_vault_pass = None
        passwords = {}
        
        # initial error check, to make sure all specified playbooks are accessible
        # before we start running anything through the playbook executor
        for playbook in self.args:
            if not os.path.exists(playbook):
                raise AnsibleError("the playbook: %s could not be found" % playbook)
            if not (os.path.isfile(playbook) or stat.S_ISFIFO(os.stat(playbook).st_mode)):
                raise AnsibleError("the playbook: %s does not appear to be a file" % playbook)

        # don't deal with privilege escalation or passwords when we don't need to
        if not self.options.listhosts and not self.options.listtasks and not self.options.listtags and not self.options.syntax:
            self.normalize_become_options()
            (sshpass, becomepass) = self.ask_passwords()
            passwords = { 'conn_pass': sshpass, 'become_pass': becomepass }

        loader = DataLoader()

        if self.options.vault_password_file:
            # read vault_pass from a file
            b_vault_pass = CLI.read_vault_password_file(self.options.vault_password_file, loader=loader)
            loader.set_vault_password(b_vault_pass)
        elif self.options.ask_vault_pass:
            b_vault_pass = self.ask_vault_passwords()
            loader.set_vault_password(b_vault_pass)

        # create the variable manager, which will be shared throughout
        # the code, ensuring a consistent view of global variables
        variable_manager = VariableManager()
        variable_manager.extra_vars = load_extra_vars(loader=loader, options=self.options)
        
#        extra_vars = {'elastic_url':Configuration.elastic_url,
#                      'uuid':self._job.uuid }
        

        variable_manager.options_vars = load_options_vars(self.options)

        # create the inventory, and filter it based on the subset specified (if any)
        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=self.options.inventory)
        
        # added by rainer@nts.at
        inventory.host_list = []
        inventory.host_list = self.options.inventory
        for group in self.inventoryContainer.groups:
            if group.name == 'all':
                if group.vars:
                    inventory.get_group('all').vars.update(group.vars)
            else:
                group.parent_groups.append(inventory.get_group('all'))
                inventory.get_group('all').child_groups.append(group)
                inventory.add_group(group) 
                
        
        variable_manager.set_inventory(inventory)

        # (which is not returned in list_hosts()) is taken into account for
        # warning if inventory is empty.  But it can't be taken into account for
        # checking if limit doesn't match any hosts.  Instead we don't worry about
        # limit if only implicit localhost was in inventory to start with.
        #
        # Fix this when we rewrite inventory by making localhost a real host (and thus show up in list_hosts())
        no_hosts = False
#        if len(inventory.list_hosts()) == 0:
            # Empty inventory
#            display.warning("provided hosts list is empty, only localhost is available")
#            no_hosts = True
        inventory.subset(self.options.subset)
#        if len(inventory.list_hosts()) == 0 and no_hosts is False:
            # Invalid limit
#            raise AnsibleError("Specified --limit does not match any hosts")

        # flush fact cache if requested
        if self.options.flush_cache:
            self._flush_cache(inventory, variable_manager)


        # create the playbook executor, which manages running the plays via a task queue manager
        self.pbex = PlaybookExecutor(playbooks=[playbook], inventory=inventory, variable_manager=variable_manager, loader=loader, options=self.options, passwords=passwords)

        results = self.pbex.run()
        self.apijob.stats = self.pbex._tqm._stats
        self.apijob.finished()

        if isinstance(results, list):
            for p in self.results:

                display.display('\nplaybook: %s' % p['playbook'])
                for idx, play in enumerate(p['plays']):
                    if play._included_path is not None:
                        loader.set_basedir(play._included_path)
                    else:
                        pb_dir = os.path.realpath(os.path.dirname(p['playbook']))
                        loader.set_basedir(pb_dir)

                    msg = "\n  play #%d (%s): %s" % (idx + 1, ','.join(play.hosts), play.name)
                    mytags = set(play.tags)
                    msg += '\tTAGS: [%s]' % (','.join(mytags))

                    if self.options.listhosts:
                        playhosts = set(inventory.get_hosts(play.hosts))
                        msg += "\n    pattern: %s\n    hosts (%d):" % (play.hosts, len(playhosts))
                        for host in playhosts:
                            msg += "\n      %s" % host

                    display.display(msg)

                    all_tags = set()
                    if self.options.listtags or self.options.listtasks:
                        taskmsg = ''
                        if self.options.listtasks:
                            taskmsg = '    tasks:\n'

                        def _process_block(b):
                            taskmsg = ''
                            for task in b.block:
                                if isinstance(task, Block):
                                    taskmsg += _process_block(task)
                                else:
                                    if task.action == 'meta':
                                        continue

                                    all_tags.update(task.tags)
                                    if self.options.listtasks:
                                        cur_tags = list(mytags.union(set(task.tags)))
                                        cur_tags.sort()
                                        if task.name:
                                            taskmsg += "      %s" % task.get_name()
                                        else:
                                            taskmsg += "      %s" % task.action
                                        taskmsg += "\tTAGS: [%s]\n" % ', '.join(cur_tags)

                            return taskmsg

                        all_vars = variable_manager.get_vars(loader=loader, play=play)
                        play_context = PlayContext(play=play, options=self.options)
                        for block in play.compile():
                            block = block.filter_tagged_tasks(play_context, all_vars)
                            if not block.has_tasks():
                                continue
                            taskmsg += _process_block(block)

                        if self.options.listtags:
                            cur_tags = list(mytags.union(all_tags))
                            cur_tags.sort()
                            taskmsg += "      TASK TAGS: [%s]\n" % ', '.join(cur_tags)

                        display.display(taskmsg)

            return 0
        else:
            return results