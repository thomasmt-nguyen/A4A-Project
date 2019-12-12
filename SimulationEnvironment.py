from SimulationProxy import ServerProxy
from DataProxy import DataProxy
from HomeAgent import HomeAgent
from ScoutAgent import ScoutAgent
from AssistantAgent import AssistantAgent
from Agent import Agent

environment = {'Test1': '0',
               'Test2': '1',
               'HW1': '2',
               'HW2': '3'}

env_name_mapping = {
    'TEST1': 'Test1',
    'TEST2': 'Test2',
    'HW1': 'HW1',
    'HW2': 'HW2'
}

class SimulationEnvironment():

    def __init__(self):
        self.dataProxy = DataProxy()
        self.status = dict.fromkeys(range(4), False)

    def get_health(self):
        return self.status

    def stop_simulation(self, env_name):
        env_id = environment[env_name_mapping[env_name.upper()]]
        self.status[env_id] = False

    def run_test1_simulation(self):
        proxy = ServerProxy("Test1")
        proxy.create()
        agent1 = Agent(proxy, agent_id=0)
        agent_list = list()
        agent_list.append(agent1)
        self.execute(agent_list, proxy)


    def run_test2_simulation(self):
        proxy = ServerProxy("Test2")
        proxy.create()
        agent1 = ScoutAgent(proxy, agent_id=0)
        agent2 = HomeAgent(proxy, agent_id=1)
        agent_list = list()
        agent_list.extend((agent1, agent2))
        self.execute(agent_list, proxy)


    def run_hw1_simulation(self):
        proxy = ServerProxy("HW1")
        proxy.create()
        agent1 = Agent(proxy, agent_id=0)
        agent_list = list()
        agent_list.append(agent1)
        self.execute(agent_list, proxy)

    def run_hw2_simlation(self):
        proxy = ServerProxy("HW2")
        proxy.create()
        agent1 = ScoutAgent(proxy, agent_id=0)
        agent2 = AssistantAgent(proxy, agent_id=1)
        agent3 = AssistantAgent(proxy, agent_id=2)
        agent4 = AssistantAgent(proxy, agent_id=3)
        agent5 = HomeAgent(proxy, agent_id=4)

        agent_list = list()
        agent_list.extend((agent1, agent2, agent3, agent4, agent5))
        self.execute(agent_list, proxy)

    def execute(self, agent_list, server_proxy):
        self.status[server_proxy.env_id] = True
        while self.status[server_proxy.env_id] is True:
            for agents in agent_list:
                agents.execute()
            server_proxy.step()
            self.update_simluation_info(agent_list, server_proxy)

    def update_simluation_info(self, agent_list, server_proxy):
        self.dataProxy.write_simulation_info(agent_list, server_proxy)



