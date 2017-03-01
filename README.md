# ansible-programmatic
# programmatic Interface for Ansible 2.x 

## ENVIRONMENT variables
  * REDIS_SERVER   	(optional): defaults to localhost
  * REDIS_PORT   	(optional): defaults to 6379
  * REDIS_DB   		(optional): defaults to 0
  * REDIS_ENABLED   (optional): defaults to False

## provided REST APIs
  * @app.route('/ansible/api/v1.0/startplay/<playbook>', methods=['POST'])
  	start play and set playbook YAML
  * @app.route('/ansible/api/v1.0/state/<uuid>', methods=['GET'])
  	get specific state for one play
  * @app.route('/ansible/api/v1.0/jobs', methods=['GET'])
  	list all jobs (plays)

## JSON Format for "startplay" POST body
	groups may be nested
	

```
{ "inventory": {
				"groups": {
					"ise": {
						"hosts": {
							"192.168.243.143": { 
								"vars": {
									"cisco_ise_ers_username": "api2",
									"cisco_ise_ers_password": "xxxxx"
								}
							}
						}
					}
				}		
			},
 	"options": { 
 				"forks": "2",
 				"become_methode": "sudo",
 				"verbosity": "3",
 				"connection": "ssh"
 			}
}
``

## Redis Connection
	To given groups and hosts variables can be expanded by redis cache. 
	This is an alternative to passing variables within the REST API in JSON.
	Using this keys at redis cache:
	* groupvars::[groupname] 
	* hostvars::[hostname]
	The values must be a JSON dict using this form:
	* {'var1':'value1','var2':'value2'}
	
