from flask import Flask
from DataProxy import DataProxy
from SimulationEnvironment import SimulationEnvironment
import json

app = Flask(__name__)
dataProxy = DataProxy()
environment = SimulationEnvironment()

@app.route('/info/<env_name>')
def read(env_name):
    response = dataProxy.read_agent_info(env_name)
    return response

@app.route('/info/health')
def info():
    environment.get_health()
    return json.dumps(environment.status)

@app.route('/agent_simulation/<env_name>/stop',  methods=['POST'])
def stop_simulation(env_name):
    environment.stop_simulation(env_name)
    return "Stopped environment"

@app.route('/agent_simulation/<env_name>/start', methods=['POST'])
def run_simulation(env_name):
    if env_name == 'test1':
        environment.run_test1_simulation()
    elif env_name == 'test2':
        environment.run_test2_simulation()
    elif env_name == 'hw1':
        environment.run_hw1_simulation()
    elif env_name == 'hw2':
        environment.run_hw2_simlation()

    return 'Success'

if __name__ == '__main__':
    app.run()



