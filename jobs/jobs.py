'''
Created on 12. Dez. 2016

@author: max
'''
import uuid
from ansiblejob import JobAnsible
from inventoryContainer import inventoryContainer
from uuid import UUID
from options import AnsibleOptions
from config.configuration import Configuration
from _collections import deque
import datetime
from ansible.executor.stats import AggregateStats
from PlaybookAPI import PlaybookAPI


class Job(object):
    
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.ansible_options = AnsibleOptions()
        self.starttime = datetime.datetime.now()
        self.stoptime = None
        self.playbook = None
        
    @property
    def inventory_json(self):
        return self._inventory_json
    
    @inventory_json.setter
    def inventory_json(self, value):
        self._inventory_json = value
          
    @property
    def stats(self):
        result = {}     
        try:
            result['uuid'] = str(self.uuid)
            result['processed'] = self._stats.processed
            result['failures'] = self._stats.failures
            result['changed'] = self._stats.changed
            result['ok'] = self._stats.ok
            result['finished'] = 'true'
            result['starttime'] = self.starttime
            result['stoptime'] = self.stoptime
            result['playbook'] = self.playbook
        except:
            result = {'finished':'false','uuid':str(self.uuid),'starttime':self.starttime, 'playbook': self.playbook}
        return result
    
    @stats.setter
    def stats(self, value):
        self._stats = value
        
    def finished(self):
        self.stoptime = datetime.datetime.now()
        
    def filenotfound(self):
        self._stats  = AggregateStats()
        self._stats.failures['file'] = 'playbook not found'

class JobFabric(object):
    
    def __init__(self):
        self.jc = JobContainer()
    
    def createNewJob(self):
        j = Job()
        self.jc.addJob(j.uuid, j)
        return j.uuid
    
    def getJob(self, uuid):
        return self.jc.getJob(uuid)
    
    def getJobList(self):
        return self.jc.getJobs().keys()
    
    def getJobListDetails(self):
        jobs =  self.jc.getJobs()
        result = []
        for key in jobs.keys():
            cache = jobs[key]
            result.append(cache.stats)
        return result
        
    
    def setInventory(self, uuid, inventoryJSON):
        if not uuid or not inventoryJSON:
            return
        j = self.getJob(uuid)
        j.inventory_json = inventoryJSON
        
    def setOptions(self, uuid, optionsJSON):
        if not uuid or not optionsJSON:
            return
        j = self.getJob(uuid)
        j.ansible_options.jsonoptions = optionsJSON
    
    def runAnsible(self, uuid, playbook=None):
        if not uuid:
            return
        j = self.getJob(uuid)
        invContainer = inventoryContainer(j.inventory_json)
        j.playbook = playbook
        ja = PlaybookAPI(playbook, invContainer, j)
        ja.parse()
#        ja = JobAnsible(invContainer, playbook=playbook, job=self.getJob(uuid))
        ja.start()
#        ja.run()    

class JobContainer(object):
    
    jobs = {}
    uuids = deque()

    def __init__(self):
        pass
    
    def addJob(self, uuid, job):
        if (len(self.uuids) >= Configuration.job_history):
            oldest = self.uuids.popleft()
            self.jobs.pop(oldest)
        self.uuids.append(uuid)
        self.jobs[uuid] = job
    
    def getJobs(self):
        return self.jobs
        
    def getJob(self, uuid):
        if not type(uuid) is UUID:
            uuid = UUID(uuid)
        if self.jobs.has_key(uuid):
            return self.jobs.get(uuid)
        
    