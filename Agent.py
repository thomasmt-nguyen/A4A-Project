import json
from Action import Action
from AgentState import AgentState
from AvoidState import AvoidState

X_COORDINATE = 0
Y_COORDINATE = 1
DIRECTLY_IN_FRONT = [0, 1]
DIRECTLY_LEFT = [-1, 0]
DIRECTLY_RIGHT = [0, 1]
AGENT_SCAN_DISTANCE = 2


class Agent:
    def __init__(self, proxy, agent_id):
        self.proxy = proxy
        self.agent_id = agent_id
        self.state = AgentState.SEARCH_PAYLOAD
        self.saved_state = AgentState.SEARCH_PAYLOAD
        self.avoid_state = AvoidState.TURN
        self.saved_avoid_action = Action.IDLE

    def do_stuff(self):

        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.state is AgentState.SEARCH_PAYLOAD:
            action = self.calculate_search_payload_action(response)
            if action is Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETRIEVE_PAYLOAD
            elif action is Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state is AgentState.RETRIEVE_PAYLOAD:
            coordinates = self.get_closest_payload_coordinates(response)
            action = self.calculate_action(coordinates)
            if action is Action.COMPLETE:
                action = Action.PICK_UP
                self.state = AgentState.SEARCH_HOME
            elif action is Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state is AgentState.SEARCH_HOME:
            action = self.calculate_search_home_action(response)
            if action is Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETURN_HOME
            elif action is Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state is AgentState.RETURN_HOME:
            coordinates = self.get_home_coordinates(response)
            action = self.calculate_action(coordinates)
            if action is Action.COMPLETE:
                action = Action.DROP
                self.state = AgentState.SEARCH_PAYLOAD
            elif action is Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state is AgentState.AVOID_OBJECT:
            action = self.calculate_avoid_action(response)
            if action is Action.COMPLETE:
                action = action.IDLE
                self.state = self.saved_state

        print(self.state)
        print(action)
        self.action(action)
        self.proxy.step()

    def calculate_avoid_action(self, response):
        if self.avoid_state is AvoidState.TURN:
            action = self.calculate_turn_action(response)
            self.avoid_state = AvoidState.MOVE
        elif self.avoid_state is AvoidState.MOVE:
            action = Action.MOVE_FORWARD
            self.avoid_state = AvoidState.CORRECT
        elif self.avoid_state is AvoidState.CORRECT:
            action = self.calculate_correct_action()
            self.avoid_state = AvoidState.COMPLETE
        elif self.avoid_state is AvoidState.COMPLETE:
            action = Action.COMPLETE
            self.avoid_state = AvoidState.TURN
        else:
            action = Action.IDLE

        return action

    def calculate_turn_action(self, response):

        if self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            if self.has_object_at_coordinate(response, DIRECTLY_LEFT) or self.has_wall_in_distance(response, 'L'):
                action = Action.TURN_RIGHT
                self.saved_avoid_action = Action.TURN_RIGHT
            elif self.has_object_at_coordinate(response, DIRECTLY_RIGHT) or self.has_wall_in_distance(response, 'R'):
                action = Action.TURN_LEFT
                self.saved_avoid_action = Action.TURN_LEFT
            else:
                action = Action.TURN_RIGHT
                self.saved_avoid_action = Action.TURN_LEFT
        else:
            action = Action.IDLE

        return action

    def calculate_correct_action(self):
        if self.saved_avoid_action is Action.TURN_LEFT:
            action = Action.TURN_RIGHT
        elif self.saved_avoid_action is Action.TURN_RIGHT:
            action = Action.TURN_LEFT
        else:
            action = Action.IDLE

        return action

    def calculate_search_payload_action(self, response):

        if self.has_payload_coordinates(response):
            action = Action.COMPLETE
        elif self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            action = Action.AVOID_OBJECT
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

    def calculate_search_home_action(self, response):

        if self.has_home_coordinates(response):
            action = Action.COMPLETE
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

    def calculate_payload_distance(self, coordinates):
        return abs(coordinates[0]) + abs(coordinates[1])

    def calculate_action(self, coordinates):
        if coordinates is DIRECTLY_IN_FRONT:
            action = Action.COMPLETE
        # Payload in front or behind agent
        elif coordinates[X_COORDINATE] is 0 and coordinates[Y_COORDINATE] > 0:
            action = Action.MOVE_FORWARD
        elif coordinates[X_COORDINATE] is 0 and coordinates[Y_COORDINATE] < 0:
            action = Action.TURN_LEFT
        # Payload left of right of agent or behind
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] > 0:
            action = Action.TURN_RIGHT
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] < 0:
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

    #need avoid agent state machine

    def convert_list(self, lists):
        dictionary = dict()
        for items in lists:
            dictionary[items[0]] = items[1]
        return dictionary

    def action(self, action):
        self.proxy.agent_action(agent_id=self.agent_id, action=action.value, mode=0)

    def get_closest_payload_coordinates(self, response):

        payloads_coordinates = self.get_payload_coordinates(response)
        closest_distance = -1

        for coordinates in payloads_coordinates:
            distance = self.calculate_payload_distance(coordinates)
            if closest_distance is -1:
                closest_distance = distance
                closest_coordinates = coordinates
            elif distance < closest_distance:
                closest_distance = distance
                closest_coordinates = coordinates

        return closest_coordinates

    def get_payload_coordinates(self, response):
        data = json.loads(response.text)
        return data['agentData']['Scan']['Payloads']

    def get_home_coordinates(self, response):
        data = json.loads(response.text)
        return data['agentData']['Scan']['Home'][0]

    def has_payload_coordinates(self, response):
        data = json.loads(response.text)
        if data['agentData']['Scan']['Payloads']:
            return True
        else:
            return False

    def has_home_coordinates(self, response):
        data = json.loads(response.text)
        if data['agentData']['Scan']['Home']:
            return True
        else:
            return False

    def has_wall_in_distance(self, response, direction):
        data = json.loads(response.text)
        wall_map = self.convert_list(data['agentData']['Scan']['Walls'])

        if wall_map[direction] <= AGENT_SCAN_DISTANCE:
            return True
        else:
            return False

    def has_object_at_coordinate(self, response, coordinate):
        # get home
        if self.has_home_coordinates(response):
            home_coordinates = self.get_home_coordinates(response)
            if coordinate is home_coordinates:
                return True
        # get payload
        elif self.has_payload_coordinates(response):
            payload_coordinates = self.get_payload_coordinates(response)
            if coordinate in payload_coordinates:
                return True
        # agent
    def has_payload_at_coordininate(self, ):
        return True

    def test_1_test_home_search_home(self):
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)

    def test_2_test_home_search_home(self):
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)

    def test_move(self, action):
        self.action(action=action)
        self.proxy.step()