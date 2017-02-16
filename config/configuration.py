'''
Created on 13. Feb. 2017

@author: max
'''
from xml.etree import ElementTree

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
        tree = ElementTree.parse(fileurl)
        root = tree.getroot()
        for child in root:
            if (child.tag == 'redis_host'):
                cls.redis_host = child.text
            elif (child.tag == 'redis_enabled'):
                cls.redis_enabled = bool(child.text)
            elif (child.tag == 'redis_port'):
                cls. redis_port = int(child.text)
            elif (child.tag == 'redis_db'):
                cls.redis_db = int(child.text)
            elif (child.tag == 'playbook_dir'):
                cls.playbook_dir = child.text
            elif (child.tag == 'playbook_default'):
                cls.playbook_default = child.text
            elif (child.tag == 'job_history'):
                cls.job_history = int(child.text)     
            elif (child.tag == 'elastic_url'):
                cls.elastic_url = child.text          
        
    @classmethod
    def is_redis_enabled(cls):
        return cls.redis_enabled
    
    @classmethod
    def set_debug(cls):
        cls.debug = True
        
    @classmethod
    def is_debug(cls):
        return cls.debug