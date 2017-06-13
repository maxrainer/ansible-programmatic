'''
Created on 12. Dez. 2016

@author: max
'''

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor import playbook_executor
from config.configuration import Configuration
import threading
from ansible.utils.display import Display
from options import AnsibleOptions
from ansible.errors import AnsibleFileNotFound

class JobAnsible(threading.Thread):

    def __init__(self, inventoryContainer, playbook=None, job=None):
        threading.Thread.__init__(self)
        self.inventoryContainer = inventoryContainer
        self._job = job
        if playbook: 
            self.playbook__ = playbook
        else:
            self.playbook__ = Configuration.playbook_default 
        self.pb_dir__ = Configuration.playbook_dir
        self.options = AnsibleOptions()
        self._load()        
        
    def run(self):
        try:
            self.pbx.run()
            self._job.stats = self.pbx._tqm._stats
        except AnsibleFileNotFound:
            self._job.filenotfound()
        self._job.finished()
        
        
    def _load(self):
        
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        passwords = dict(vault_pass='secret')  
        
        #display seems not to work yet :-(
        self.display = Display()
        self.display.verbosity = self.options.verbosity
        playbook_executor.display.verbosity = self.options.verbosity
        
        extra_vars = {'elastic_url':Configuration.elastic_url,
                      'uuid':self._job.uuid }  
        self.variable_manager.extra_vars = extra_vars

        self.inventory = Inventory(self.loader, self.variable_manager, self.inventoryContainer.allHosts())  
        for group in self.inventoryContainer.groups:
            if group.name == 'all':
                if group.vars:
                    self.inventory.get_group('all').vars.update(group.vars)
            else:
                group.parent_groups.append(self.inventory.get_group('all'))
                self.inventory.add_group(group)  
                
        self.variable_manager.set_inventory(self.inventory)
    
        self.playbook = "%s/%s" % (self.pb_dir__, self.playbook__)   
        
        self.pbx = playbook_executor.PlaybookExecutor(
                        playbooks=[self.playbook],
                        inventory=self.inventory,
                        variable_manager=self.variable_manager,
                        loader=self.loader,
                        options=self.options.options(),
                        passwords=passwords)
        
