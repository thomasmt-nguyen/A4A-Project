from SimulationProxy import SimluationProxy
from Agent import Agent
from Action import Action
from HomeAgent import HomeAgent
from ScoutAgent import ScoutAgent
from AssistantAgent import AssistantAgent

proxy = SimluationProxy("HW2");

#HW1_agent1 = Agent(proxy, agent_id=0)

agent1 = ScoutAgent(proxy, agent_id=0)
agent2 = AssistantAgent(proxy, agent_id=1)
agent3 = HomeAgent(proxy, agent_id=2)
agent4 = HomeAgent(proxy, agent_id=3)
agent5 = HomeAgent(proxy, agent_id=4)

#agent1.test_3_test_2()
#agent2.test_3_test_4()

'''agent2.action(Action.MOVE_FORWARD)
agent1.action(Action.IDLE)
proxy.step()

agent2.action(Action. MOVE_FORWARD)
agent1.action(Action.IDLE)
proxy.step()

agent2.action(Action. MOVE_FORWARD)
agent1.action(Action.IDLE)
proxy.step()'''

while True:
    agent1.do_stuff()
    agent2.do_stuff()
    agent3.do_stuff()
    agent4.action(Action.IDLE)
    agent5.action(Action.IDLE)
    response = proxy.step()
    print(response.json())
