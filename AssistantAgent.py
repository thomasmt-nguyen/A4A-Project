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
        Agent.__init__(self, proxy, agent_id)
        self.state = AgentState.SEARCH_AGENT
        self.saved_state = AgentState.SEARCH_AGENT
        self.type = "Assistant"

    def execute(self):
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
            if not self.has_target_agent_coordinates(response):
                action = Action.IDLE
                self.state = AgentState.SEARCH_AGENT
            else:
                # if case for no more agent on map. go back to search for agent
                coordinates = self.get_target_agent_coordinates(response)
                action = self.calculate_move_to_agent_action(response, coordinates)
                if action == Action.COMPLETE and self.has_payload(response):
                    action = Action.DROP
                    self.increment_completion()
                    self.state = AgentState.WAIT_FOR_PAYLOAD
                    self.dropped_payload_coordinates = DIRECTLY_IN_FRONT
                elif action == Action.COMPLETE and not self.has_payload(response):
                    action = Action.IDLE
                    self.state = AgentState.WAIT_FOR_PAYLOAD
                elif action == Action.AVOID_OBJECT:
                    action = action.IDLE
                    self.saved_state = self.state
                    self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.WAIT_FOR_PAYLOAD:
            # TODO: Delete this and use other payload coordinate?
            if self.has_new_payload_coordinates(response):
                action = self.caculate_wait_for_payload_action(response)
                if action == Action.COMPLETE:
                    action = Action.IDLE
                    self.state = AgentState.RETRIEVE_PAYLOAD
            else:
                action = Action.IDLE

        elif self.state == AgentState.RETRIEVE_PAYLOAD:
            if not self.has_new_payload_coordinates(response):
                action = Action.IDLE
                self.state = AgentState.WAIT_FOR_PAYLOAD
            else:
                coordinates = self.get_closest_payload_coordinates(response)
                action = self.calculate_retrieve_payload_action(coordinates)
                if action == Action.COMPLETE:
                    action = Action.PICK_UP
                    self.state = AgentState.SEARCH_AGENT
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

        if self.dropped_payload_coordinates:
            self.update_last_dropped_package_coordinates(action)
        #print(f"Assistant agent : {self.state}")
        #print(f"Assistant agent : {action}")

        self.action(action)
        self.last_action = action

    def calculate_move_to_agent_action(self, response, coordinates):

        if coordinates == IN_FRONT and self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            action = Action.AVOID_OBJECT
        elif coordinates == CORNER_RIGHT and self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            action = Action.TURN_RIGHT
        elif coordinates == CORNER_LEFT and self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            action = Action.TURN_LEFT
        else:
            within_range = [IN_FRONT, CORNER_RIGHT, CORNER_LEFT]
            if coordinates in within_range and self.get_target_agent_ready_status(response):
                action = Action.COMPLETE
                self.in_position = True
            elif coordinates in within_range and not self.get_target_agent_ready_status(response):
                action = Action.IDLE
            elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] < 0 and not self.has_object_at_coordinate(response, DIRECTLY_LEFT):
                action = Action.TURN_LEFT
            # Payload left of right of agent or behind
            elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] > 0 and not self.has_object_at_coordinate(response, DIRECTLY_RIGHT):
                action = Action.TURN_RIGHT
            elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] < 0 and not self.has_object_at_coordinate(response, DIRECTLY_LEFT):
                action = Action.TURN_LEFT
            elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] > 0:
                action = Action.MOVE_FORWARD
            else:
                action = Action.MOVE_FORWARD

            # Payload in front or behind agent
            if action == Action.MOVE_FORWARD and self.has_possible_collision(response):
                action = Action.AVOID_OBJECT
        return action


    def calculate_search_for_agent_action(self, response):
        if self.has_target_agent_coordinates(response):
            action = Action.COMPLETE
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'R'):
            action = Action.TURN_LEFT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_RIGHT
        elif self.has_possible_collision(response):
            action = Action.AVOID_OBJECT
        else:
            action = Action.MOVE_FORWARD

        return action

    def calculate_retrieve_payload_action(self, coordinates):
        if coordinates == DIRECTLY_IN_FRONT:
            action = Action.COMPLETE
        # Payload in front or behind agent
        # Payload left of right of agent or behind
        elif coordinates[X_COORDINATE] >= 0:
            action = Action.TURN_RIGHT
        elif coordinates[X_COORDINATE] < 0:
            action = Action.TURN_LEFT
        else:
            print("Error: No Action")
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