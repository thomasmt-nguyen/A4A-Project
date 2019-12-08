from SimulationProxy import SimluationProxy
from Agent import Agent
from Agent import Action

proxy = SimluationProxy("HW1");

env_id = 0;
agent_id = 0;

# data = proxy.create();
# data = proxy.agent_action(agent_id=agent_id, action="drop", mode=0)
# data2 = proxy.step()
# print(data.json());
# print(data2.json());

agent = Agent(proxy)

#agent.test_1_test_home_search_home()

while True:
    agent.do_stuff()
