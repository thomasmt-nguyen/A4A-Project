from SimulationProxy import SimluationProxy
from Agent import Agent

proxy = SimluationProxy("HW2");

agent1 = Agent(proxy, agent_id=0)
agent2 = Agent(proxy, agent_id=1)
agent3 = Agent(proxy, agent_id=2)
agent4 = Agent(proxy, agent_id=3)
agent5 = Agent(proxy, agent_id=4)

# agent.test_2_test_home_search_home()

while True:
    agent1.do_stuff()
    agent2.do_stuff()
    agent3.do_stuff()
    agent4.do_stuff()
    agent5.do_stuff()
    response = proxy.step()
    print(response.json())
