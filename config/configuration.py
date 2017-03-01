'''
Created on 13. Feb. 2017

@author: max
'''
from xml.etree import ElementTree
import os

class Configuration(object):
    
    redis_enabled = False
    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    playbook_dir = "/etc/ansible"
    playbook_default = "site.yaml"
    job_history = 20
    elastic_url = 'http://localhost:9920'
    
    debug = False
    
    def __init__(self):
        pass
    
    @classmethod
    def read_config(cls, fileurl):
        cls.redis_host = os.getenv('REDIS_SERVER', 'localhost')
        cls.redis_port = os.getenv('REDIS_PORT', 6379)
        cls.redis_db = os.getenv('REDIS_DB', 0)
        cls.redis_enabled = os.getenv('REDIS_ENABLED', False)
        
        tree = ElementTree.parse(fileurl)
        root = tree.getroot()
        for child in root:
            if (child.tag == 'playbook_dir'):
                cls.playbook_dir = child.text
            elif (child.tag == 'playbook_default'):
                cls.playbook_default = child.text
            elif (child.tag == 'job_history'):
                cls.job_history = int(child.text)       
        
    @classmethod
    def is_redis_enabled(cls):
        return cls.redis_enabled
    
    @classmethod
    def set_debug(cls):
        cls.debug = True
        
    @classmethod
    def is_debug(cls):
        return cls.debug
    