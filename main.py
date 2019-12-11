from flask import Flask
from pymongo import MongoClient

from SimulationProxy import ServerProxy
from DataProxy import DataProxy
from HomeAgent import HomeAgent
from ScoutAgent import ScoutAgent
from AssistantAgent import AssistantAgent
from Agent import Agent

app = Flask(__name__)
dataProxy = DataProxy()

@app.route('/stuff')
def write():
    dataProxy.write("stuff")
    return 'Writing to database'

@app.route('/agent_simulation/<env_name>')
def hello_world(env_name):
    post = {"_id": 0, "name": "Thomas", "Score":5}
    return f'{env_name}'


@app.route('/agent_simulation/<env_name>', methods=['POST'])
def run_simulation(env_name):
    if env_name == 'test1':
        run_test1_simulation()
    elif env_name == 'test2':
        run_test2_simulation()
    elif env_name == 'hw1':
        run_hw1_simulation()
    elif env_name == 'hw2':
        run_hw2_simlation()

    return 'Success'


def run_test1_simulation():
    proxy = ServerProxy("Test1")
    agent1 = Agent(proxy, agent_id=0)
    while agent1.completeded_packages != 2:
        agent1.execute()
        proxy.step()


def run_test2_simulation():
    proxy = ServerProxy("Test2")
    agent1 = ScoutAgent(proxy, agent_id=0)
    agent2 = HomeAgent(proxy, agent_id=1)
    while True:
        agent1.execute()
        agent2.execute()
        proxy.step()


def run_hw1_simulation():
    proxy = ServerProxy("HW1")
    agent1 = ScoutAgent(proxy, agent_id=0)
    while True:
        agent1.execute()
        proxy.step()

def run_hw2_simlation():
    proxy = ServerProxy("HW2")
    agent1 = ScoutAgent(proxy, agent_id=0)
    agent2 = AssistantAgent(proxy, agent_id=1)
    agent3 = AssistantAgent(proxy, agent_id=2)
    agent4 = AssistantAgent(proxy, agent_id=3)
    agent5 = HomeAgent(proxy, agent_id=4)

    while True:
        agent1.execute()
        agent2.execute()
        agent3.execute()
        agent4.execute()
        agent5.execute()
        proxy.step()

if __name__ == '__main__':
    app.run()



