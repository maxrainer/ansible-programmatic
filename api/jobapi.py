'''
Created on 12. Dez. 2016

@author: max
'''
from flask import Flask
from flask.json import jsonify
from jobs.jobs import JobFabric
from flask import request
from flask.helpers import make_response
from optparse import OptionParser
import re
from config.configuration import Configuration
from scipy.optimize._tstutils import methods

app = Flask(__name__)

@app.route('/ansible/api/v1.0/jobs', methods=['GET'])
def get_jobs():
    cf = JobFabric()
    return jsonify({'jobs': cf.getJobList()})

    
@app.route('/testing', methods=['GET'])
def testing():
    return jsonify(origin=request.headers.get('X-Forwarded-For', request.host))
    
@app.route('/ansible/api/v1.0/startplay/<playbook>', methods=['POST'])
def start_play(playbook):
    inventoryJSON = request.json['inventory']
    optionsJSON = request.json['options']
    cf = JobFabric()
    uuid = cf.createNewJob()
    cf.setInventory(uuid, inventoryJSON)
    cf.setOptions(uuid, optionsJSON)
    cf.runAnsible(uuid, playbook)
    stateurl = request.host_url + 'ansible/api/v1.0/state/' + str(uuid)
    return jsonify({'job': uuid, 'state_url': stateurl})

@app.route('/ansible/api/v1.0/state/<uuid>', methods=['GET'])
def get_state(uuid):
    cf = JobFabric()
    job = cf.getJob(uuid)
    if not job.stats:
        return jsonify({'state': 'running'})
    return jsonify({'state': job.stats})   

@app.route('/ansible/api/v1.0/jobsdetail', methods=['GET'])
def get_jobdetail():
    cf = JobFabric()
    jobs = cf.getJobListDetails()
    return jsonify({'jobs': jobs})
      

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': "maybe missing parameter"}))

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'internal server error: ' + error.message }))

def input_parser():
    parser = OptionParser("jobapi.py -c [config File] -d")
    parser.add_option("-c", "--config", default=None, dest="configfile", help="[REQUIRED]config File")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="debug" ) 
    (opts, args) = parser.parse_args()
    
    missing_options = []
    for option in parser.option_list:
        if re.match(r'^\[REQUIRED\]', option.help) and eval('opts.' + option.dest) == None:
            missing_options.extend(option._long_opts)
    if len(missing_options) > 0:
        parser.error('Missing REQUIRED parameters: ' + str(missing_options))
    return opts;

if __name__ == '__main__':
    opts = input_parser()
    option_dict = vars(opts)
    Configuration.read_config(option_dict.get('configfile'))
    if option_dict.get('debug'):
        Configuration.set_debug()
    app.run (debug=Configuration.is_debug(), host='0.0.0.0', port=5000)
    
    
    