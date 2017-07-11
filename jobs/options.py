'''
Created on 14. Feb. 2017

@author: max
'''
import optparse

class AnsibleOptions(object):
    
    """
    Options class to replace Ansible OptParser
    """
    
    def __init__(self, verbosity=0, inventory=None, listhosts=None, subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None, new_vault_password_file=None,
                 output_file=None, tags=None, skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None, connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None, poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None, force_handlers=None, flush_cache=None, listtasks=None, listtags=None, module_path=None):
        self.verbosity = 1
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = []
        self.forks = 5
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
#        self.tags = tags
#        self.skip_tags = skip_tags
#        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = 'paramiko'
        self.timeout = 2
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = ""
        self.ssh_extra_args = ""
#        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path
        
        self.inventory = "ise,"
        self.skip_tags = []
        self.su = False
        self.su_user = None
        self.tags = ["all"]
        
        
        self.jsonoptions = {}
        
        
    def options(self):
        if self.jsonoptions:
            if 'forks' in self.jsonoptions:
                self.forks = int(self.jsonoptions['forks'])
            if 'verbosity' in self.jsonoptions:
                self.verbosity = int(self.jsonoptions['verbosity'])
            if 'become_methode' in self.jsonoptions:
                self.become_method = self.jsonoptions['become_methode']
            if 'become' in self.jsonoptions:
                self.become = self.jsonoptions['become']
            if 'connection' in self.jsonoptions:
                self.connection = self.jsonoptions['connection']  
            if 'timeout' in self.jsonoptions:
                self.timeout = int(self.jsonoptions['timeout'])             
        return self
    
    def get_verbosity(self):
        if self.jsonoptions:
            if 'verbosity' in self.jsonoptions:
                return self.jsonoptions['verbosity']
        return self.verbosity
            