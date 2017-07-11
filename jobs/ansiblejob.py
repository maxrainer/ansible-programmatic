'''
Created on 12. Dez. 2016

@author: max
'''

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from config.configuration import Configuration
import threading
from ansible.utils.display import Display
from options import AnsibleOptions
from ansible.errors import AnsibleFileNotFound

from ansible.cli import CLI
from ansible.cli.playbook import PlaybookCLI

class JobAnsible(CLI):

    def __init__(self, inventoryContainer, playbook=None, job=None):
#        threading.Thread.__init__(self)
        self.inventoryContainer = inventoryContainer
        self._job = job
        if playbook: 
            self.playbook__ = playbook
        else:
            self.playbook__ = Configuration.playbook_default 
        self.pb_dir__ = Configuration.playbook_dir
 #       self.options = AnsibleOptions()
 
        self.options = None
        self.parser = None
        self.action = None
        self.callback = None
        
        self.parse()
        self._load()   
        
    def parse(self):
        parser = super(JobAnsible, self).base_parser(usage="API", inventory_opts=True)     
        self.parser = parser
        self.args = []
        super(JobAnsible, self).parse()
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
        self.options.inventory = 'ise,'
        self.options.skip_tags = []
        self.options.extra_vars = []
        self.options.force_handlers = False
        self.options.start_at_task = None
        self.options.step = None
        self.options.subset = None
        self.options.verbosity = 3
        self.options.timeout = 5     
        
        
    def run(self):
        try:
#            pbx.run()
            self._job.stats = self.pbx._tqm._stats
        except AnsibleFileNotFound:
            self._job.filenotfound()
        self._job.finished()
        
        
    def _load(self):
        
        variable_manager = VariableManager()
        variable_manager.extra_vars = {}
        variable_manager.options_vars = {'ansible_check_mode' : False}
        
        loader = DataLoader()
        passwords = dict(vault_pass='secret')  
        
        
        #display seems not to work yet :-(
        display = Display()
        display.verbosity = self.options.verbosity
#        playbook_executor.display.verbosity = self.options.verbosity
        
        extra_vars = {'elastic_url':Configuration.elastic_url,
                      'uuid':self._job.uuid }  
        self.variable_manager.extra_vars = extra_vars

        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=self.inventoryContainer.allHosts())  
        for group in self.inventoryContainer.groups:
            if group.name == 'all':
                if group.vars:
                    inventory.get_group('all').vars.update(group.vars)
            else:
                group.parent_groups.append(inventory.get_group('all'))
                inventory.add_group(group)  
                
        variable_manager.set_inventory(inventory)
        playbook = "%s/%s" % (self.pb_dir__, self.playbook__)   
        
        pbx = PlaybookExecutor(
                             playbooks=[playbook],
                             inventory=inventory,
                             variable_manager=variable_manager,
                             loader=loader,
                             options=self.options,
                             passwords=passwords)
        pbx.run()
        
