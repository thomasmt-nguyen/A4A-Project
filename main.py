from SimulationProxy import SimluationProxy
from Agent import Agent

proxy = SimluationProxy("Test1");

agent = Agent(proxy, agent_id=0)

# agent.test_2_test_home_search_home()

while True:
    agent.do_stuff()
