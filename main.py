from SimulationProxy import SimluationProxy
from Agent import Agent
from Action import Action
from HomeAgent import HomeAgent
from ScoutAgent import ScoutAgent
from AssistantAgent import AssistantAgent
from OtherAgent import OtherAgent
from OtherAgent import Coordinate

proxy = SimluationProxy("HW2");

agent1 = ScoutAgent(proxy, agent_id=0)
agent2 = AssistantAgent(proxy, agent_id=1)
agent3 = HomeAgent(proxy, agent_id=2)
agent4 = HomeAgent(proxy, agent_id=3)
agent5 = HomeAgent(proxy, agent_id=4)

while True:
    agent1.do_stuff()
    agent2.do_stuff()
    agent3.do_stuff()
    agent4.action(Action.IDLE)
    agent5.action(Action.IDLE)
    response = proxy.step()
    print(response.json())
