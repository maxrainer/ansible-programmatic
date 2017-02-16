'''
Created on 16. Dez. 2016

@author: max
'''
from ansible.inventory.group import Group
from ansible.inventory import host
from config.configuration import Configuration
import redis
import json

class inventoryContainer(object):
    
    def __init__(self, jsonIn):
        self._inv = jsonIn
        if Configuration.is_redis_enabled():
            self._redis = redis.StrictRedis(host=Configuration.redis_host, port=Configuration.redis_port, db=Configuration.redis_db)
        self._groups = []
        self._hosts = {}
        self._parse()
        
      
    def _parse(self):  
        for groupname in self._inv["groups"]:
            root = Group(groupname)
            self._groups.append(root)
            self._forward(self._inv["groups"][groupname], root)
                

    def _forward(self, fwd, parentgroup):
        if "groups" in fwd:
            for child in fwd["groups"]:
                childgroup = Group(child)
                parentgroup.add_child_group(childgroup)
                self._forward(fwd["groups"][child], childgroup)
        
        if "hosts" in fwd:
            for hostname in fwd["hosts"]:
                    if not hostname in self._hosts:
                        self._hosts[hostname] = host.Host(hostname)
                    h = self._hosts[hostname]
                    parentgroup.add_host(h)
                    
                    if "vars" in fwd["hosts"][hostname]:
                        h.vars = fwd["hosts"][hostname]["vars"]
                    merged = self._redis_vars(hostname, h.vars, group=False)
                    h.vars = merged
        
        if "vars" in fwd:
            parentgroup.vars = fwd["vars"]
        merged = self._redis_vars(parentgroup.name, parentgroup.vars, group=True)
        parentgroup.vars = merged
        
    def _redis_vars(self, name, mastervars, group=False):
        if not Configuration.is_redis_enabled():
            return mastervars
        r_key = "groupvars::" + name if group else "hostvars::" + name 
        r_vars = self._redis.get(r_key)
        if not r_vars:
            return mastervars
        r_json = json.loads(r_vars)
        result = self._merge_dicts(mastervars, r_json)
        return result
        
    @property
    def groups(self):
        return self._groups
    
    def allHosts(self):
        result = []
        for host in self._hosts.values():
            result.append(host.name)
        return result
    
    def _merge_dicts(self, *dicts):
        result = {}
        for dictionary in dicts:
            if dict:
                result.update(dictionary)
        return result