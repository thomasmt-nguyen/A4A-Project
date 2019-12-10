from Action import Action
from Agent import Agent
from AgentState import AgentState
from AvoidState import AvoidState
import json

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


class AssistantAgent(Agent):

    def __init__(self, proxy, agent_id):
        self.proxy = proxy
        self.agent_id = agent_id
        self.state = AgentState.SEARCH_AGENT
        self.saved_state = AgentState.SEARCH_AGENT
        self.avoid_state = AvoidState.TURN
        self.saved_avoid_action = Action.IDLE
        self.home_coordinates = ()

    def do_stuff(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.state == AgentState.SEARCH_AGENT:
            action = self.calculate_search_for_agent_action(response)
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.MOVE_TO_AGENT
            elif action == Action.AVOID_OBJECT:
                action = action.IDLE
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT


        elif self.state == AgentState.MOVE_TO_AGENT:
            if not self.has_agent_coordinates(response):
                action = Action.IDLE
                self.state = AgentState.SEARCH_AGENT
            else:
                # if case for no more agent on map. go back to search for agent
                coordinates = self.get_target_agent_coordinates(response)
                action = self.calculate_move_to_agent_action(response, coordinates)
                if action == Action.COMPLETE and self.has_payload(response):
                    action = Action.DROP
                    self.state = AgentState.WAIT_FOR_PAYLOAD
                elif action == Action.COMPLETE and not self.has_payload(response):
                    action = Action.IDLE
                    self.state = AgentState.WAIT_FOR_PAYLOAD
                elif action == Action.AVOID_OBJECT:
                    action = action.IDLE
                    self.saved_state = self.state
                    self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.WAIT_FOR_PAYLOAD:
            coordinates = self.get_closest_payload_coordinates(response)
            action = self.caculate_wait_for_payload_action(coordinates)
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETRIEVE_PAYLOAD

        elif self.state == AgentState.RETRIEVE_PAYLOAD:
            coordinates = self.get_closest_payload_coordinates(response)
            action = self.calculate_retrieve_payload_action(coordinates)
            if action == Action.COMPLETE:
                action = Action.PICK_UP
                self.state = AgentState.SEARCH_HOME

        elif self.state == AgentState.AVOID_OBJECT:
            action = self.calculate_avoid_object_action(response)
            if action == Action.COMPLETE:
                action = action.IDLE
                self.state = self.saved_state
        else:
            print("Error: No State")
            action = Action.IDLE

        print(f"Home agent : {self.state}")
        print(f"Home agent : {action}")

        self.action(action)

    def calculate_move_to_agent_action(self, response, coordinates):
        if coordinates == DIRECTLY_IN_FRONT:
            action = Action.COMPLETE
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] < 0:
            action = Action.TURN_LEFT
        # Payload left of right of agent or behind
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] > 0:
            action = Action.TURN_RIGHT
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] < 0:
            action = Action.TURN_LEFT
            # Payload in front or behind agent
        elif self.has_possible_collision(response):
            action = Action.AVOID_OBJECT
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] > 0:
            action = Action.MOVE_FORWARD
        else:
            action = Action.MOVE_FORWARD

        return action

    def get_target_agent_coordinates(self, response):
        data = json.loads(response.text)
        agents = data['agentData']['Scan']['Agents']

        for agent in agents:
            agent_status = self.read_mode(agent['Status'])
            if agent_status.agent_id == self.agent_id + 1:
                return tuple(agent['Loc'])


    def calculate_search_for_agent_action(self, response):
        if self.has_target_agent_coordinates(response):
            action = Action.COMPLETE
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        elif self.has_possible_collision(response):
            action = Action.AVOID_OBJECT
        else:
            action = Action.MOVE_FORWARD

        return action

    def has_target_agent_coordinates(self, response):

        if not self.has_agent_coordinates(response):
            return False

        data = json.loads(response.text)
        agents = data['agentData']['Scan']['Agents']

        for agent in agents:
            agent_status = self.read_mode(agent['Status'])
            if agent_status.agent_id == self.agent_id + 1:
                return True

        return False

    def calculate_retrieve_payload_action(self, coordinates):
        if coordinates == DIRECTLY_IN_FRONT:
            action = Action.COMPLETE
        # Payload in front or behind agent
        # Payload left of right of agent or behind
        elif coordinates[X_COORDINATE] > 0:
            action = Action.TURN_RIGHT
        elif coordinates[X_COORDINATE] < 0:
            action = Action.TURN_LEFT
        else:
            print("Error: No Action")
            action = Action.IDLE

        return action

    def caculate_wait_for_payload_action(self, coordinates):

        within_range = [DIRECTLY_IN_FRONT, DIRECTLY_BEHIND, DIRECTLY_RIGHT, DIRECTLY_LEFT]

        if coordinates in within_range:
            action = Action.COMPLETE
        else:
            action = Action.IDLE

        return action

        print(f"{self.agent_id}: {self.state}")
        print(f"{self.agent_id}: {action}")
        self.action(action)
