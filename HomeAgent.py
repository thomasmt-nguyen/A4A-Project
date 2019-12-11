from Action import Action
from Agent import Agent
from AgentState import AgentState

X_COORDINATE = 0
Y_COORDINATE = 1
IN_FRONT = (0, 2)
DIRECTLY_IN_FRONT = (0, 1)
DIRECTLY_BEHIND = (0, -1)
DIRECTLY_LEFT = (-1, 0)
DIRECTLY_RIGHT = (1, 0)
CORNER_RIGHT = (1, 1)
CORNER_LEFT = (-1, 1)
AGENT_SCAN_DISTANCE = 1

class HomeAgent(Agent):

    def __init__(self, proxy, agent_id):
        Agent.__init__(self, proxy, agent_id)
        self.state = AgentState.SEARCH_HOME
        self.saved_state = AgentState.SEARCH_HOME

    def execute(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.state == AgentState.SEARCH_HOME:
            action = self.calculate_search_home_action(response)
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETURN_HOME
            elif action == Action.AVOID_OBJECT:
                action = action.IDLE
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.RETURN_HOME:
            coordinates = self.get_home_coordinates(response)
            action = self.calculate_return_home_action(response, coordinates)
            if action == Action.COMPLETE and self.has_payload(response):
                action = Action.DROP
                self.increment_completion()
                self.state = AgentState.WAIT_FOR_PAYLOAD
            elif action == Action.COMPLETE and not self.has_payload(response):
                action = Action.IDLE
                self.state = AgentState.WAIT_FOR_PAYLOAD
            elif action == Action.AVOID_OBJECT:
                action = action.IDLE
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.WAIT_FOR_PAYLOAD:
            action = self.caculate_wait_for_payload_action(response)
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETRIEVE_PAYLOAD

        elif self.state == AgentState.RETRIEVE_PAYLOAD:
            if not self.has_payload_coordinates(response):
                action = Action.IDLE
                self.state = AgentState.WAIT_FOR_PAYLOAD
            else:
                action = self.calculate_retrieve_payload_action(response)
                if action == Action.COMPLETE:
                    action = Action.PICK_UP
                    self.state = AgentState.SEARCH_HOME
                elif action == Action.AVOID_OBJECT:
                    action = action.IDLE
                    self.saved_state = self.state
                    self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.AVOID_OBJECT:
            action = self.calculate_avoid_object_action(response)
            if action == Action.COMPLETE:
                action = action.IDLE
                self.state = self.saved_state
        else:
            print("Error: No State")
            action = Action.IDLE

        #print(f"Home agent : {self.state}")
        #print(f"Home agent : {action}")

        self.action(action)

    def calculate_retrieve_payload_action(self, response):

        if self.has_payload_coordinates(response):
            coordinates = self.get_closest_payload_coordinates(response)
            if coordinates == DIRECTLY_IN_FRONT:
                action = Action.COMPLETE
            elif coordinates[X_COORDINATE] >= 0:
                action = Action.TURN_RIGHT
            elif coordinates[X_COORDINATE] < 0:
                action = Action.TURN_LEFT
            else:
                print("Error: No Action")
                action = Action.IDLE
        else:
            action = Action.IDLE

        return action

    def caculate_wait_for_payload_action(self, response):

        if not self.has_payload_coordinates(response):
            action = Action.IDLE
        else:
            coordinates = self.get_closest_payload_coordinates(response)
            within_range = [DIRECTLY_IN_FRONT, DIRECTLY_BEHIND, DIRECTLY_RIGHT, DIRECTLY_LEFT]

            if coordinates in within_range:
                action = Action.COMPLETE
            else:
                action = Action.IDLE

        return action
