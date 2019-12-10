from SimulationProxy import SimluationProxy
from HomeAgent import HomeAgent
from ScoutAgent import ScoutAgent
from AssistantAgent import AssistantAgent
from Action import Action

proxy = SimluationProxy("HW2");

agent1 = ScoutAgent(proxy, agent_id=0)
agent2 = AssistantAgent(proxy, agent_id=1)
agent3 = AssistantAgent(proxy, agent_id=2)
agent4 = AssistantAgent(proxy, agent_id=3)
agent5 = HomeAgent(proxy, agent_id=4)

agent1.action(Action.DROP)
agent2.do_stuff()
agent3.do_stuff()
agent4.do_stuff()
agent5.do_stuff()
response = proxy.step()


while True:
    agent1.do_stuff()
    agent2.do_stuff()
    agent3.do_stuff()
    agent4.do_stuff()
    agent5.do_stuff()
    response = proxy.step()
    print(response.json())
