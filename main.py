from flask import Flask
from DataProxy import DataProxy
from SimulationEnvironment import SimulationEnvironment

app = Flask(__name__)
dataProxy = DataProxy()
environment = SimulationEnvironment()

@app.route('/info/<env_name>')
def write(env_name):
    response = dataProxy.read_agent_info(env_name)
    return response

@app.route('/agent_simulation/<env_name>', methods=['POST'])
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



