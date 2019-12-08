import json
from enum import Enum

payload_map = {}
X_COORDINATE = 0
Y_COORDINATE = 1
DIRECTLY_IN_FRONT = [0, 1]
DIRECTLY_LEFT = [-1, 0]
DIRECTLY_RIGHT = [0, 1]
AGENT_SCAN_DISTANCE = 2


class Agent:
    def __init__(self, proxy):
        self.proxy = proxy
        self.env_id = "2"
        self.agent_id = 0
        self.state = AGENT_STATE.SEARCH_PAYLOAD
        self.saved_state = AGENT_STATE.SEARCH_PAYLOAD
        self.avoid_state = AVOID_STATE.TURN
        self.saved_avoid_action = Action.IDLE

    def do_stuff(self):

        if self.state == AGENT_STATE.SEARCH_PAYLOAD:
            action = self.determine_search_payload_action()
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AGENT_STATE.RETRIEVE_PAYLOAD
            elif action == Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AGENT_STATE.AVOID_OBJECT
        elif self.state == AGENT_STATE.RETRIEVE_PAYLOAD:
            coordinates = self.get_closest_payload_coordinates()
            action = self.determine_action(coordinates)
            if action == Action.COMPLETE:
                action = Action.PICK_UP
                self.state = AGENT_STATE.SEARCH_HOME
            elif action == Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AGENT_STATE.AVOID_OBJECT
        elif self.state == AGENT_STATE.SEARCH_HOME:
            action = self.determine_search_home_action()
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AGENT_STATE.RETURN_HOME
            elif action == Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AGENT_STATE.AVOID_OBJECT
        elif self.state == AGENT_STATE.RETURN_HOME:
            coordinates = self.get_home_coordinates()
            action = self.determine_action(coordinates)
            if action == Action.COMPLETE:
                action = Action.DROP
                self.state = AGENT_STATE.SEARCH_PAYLOAD
            elif action == Action.AVOID_OBJECT:
                self.saved_state = self.state
                self.state = AGENT_STATE.AVOID_OBJECT
        elif self.state == AGENT_STATE.AVOID_OBJECT:
            action = self.determine_avoid_action()
            if action == Action.COMPLETE:
                action = action.IDLE
                self.state = self.saved_state

        print(self.state)
        print(action)
        self.action(action)
        self.proxy.step()

    def determine_avoid_action(self):
        if self.avoid_state == AVOID_STATE.TURN:
            action = self.determine_turn_action()
            self.avoid_state = AVOID_STATE.MOVE
        elif self.avoid_state == AVOID_STATE.MOVE:
            action = Action.MOVE_FORWARD
            self.avoid_state = AVOID_STATE.CORRECT
        elif self.avoid_state == AVOID_STATE.CORRECT:
            action = self.determine_correct_action()
            self.avoid_state = AVOID_STATE.COMPLETE
        elif self.avoid_state == AVOID_STATE.COMPLETE:
            action = Action.COMPLETE
            self.avoid_state = AVOID_STATE.TURN
        else:
            action = Action.IDLE

        return action

    def determine_turn_action(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)

        action = Action.IDLE
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

        return action

    def determine_correct_action(self):
        if self.saved_avoid_action == Action.TURN_LEFT:
            action = Action.TURN_RIGHT
        elif self.saved_avoid_action == Action.TURN_RIGHT:
            action = Action.TURN_LEFT
        else:
            action = Action.IDLE

        return action

    def determine_search_payload_action(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.has_payload_coordinates(response):
            action = Action.COMPLETE
        # is has object in front... move right
        elif self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            action = Action.AVOID_OBJECT
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

    def determine_search_home_action(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.has_home_coordinates(response):
            action = Action.COMPLETE
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

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
            home_coordinates = self.get_home_coordinates()
            if home_coordinates == coordinate:
                return True
        # get payload
        elif self.has_payload_coordinates(response):
            payload_coordinates = self.get_closest_payload_coordinates()
            if payload_coordinates == coordinate:
                return True
        # agent

    def convert_list(self, lists):
        dictionary = dict()
        for items in lists:
            dictionary[items[0]] = items[1]
        return dictionary

    def action(self, action):
        self.proxy.agent_action(agent_id=self.agent_id, action=action.value, mode=0)

    def determine_action(self, coordinates):
        if coordinates == DIRECTLY_IN_FRONT:
            action = Action.COMPLETE
        # Payload in front or behind agent
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] > 0:
            action = Action.MOVE_FORWARD
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] < 0:
            action = Action.TURN_LEFT
        # Payload left of right of agent or behind
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] > 0:
            action = Action.TURN_RIGHT
        elif coordinates[Y_COORDINATE] <= 0 and coordinates[X_COORDINATE] < 0:
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        return action

    def get_closest_payload_coordinates(self):
        data = self.proxy.agent_status(agent_id=self.agent_id)

        print(self.has_payload_coordinates(data))
        payloads_coordinates = self.extract_payload_coordinates(data)

        closest_payload_distance = -1;

        for coordinates in payloads_coordinates:
            distance = self.calculate_payload_distance(coordinates)
            if closest_payload_distance == -1:
                closest_payload_distance = distance
                closest_payload_coordinates = coordinates
            elif distance < closest_payload_distance:
                closest_payload_distance = distance
                closest_payload_coordinates = coordinates

        return closest_payload_coordinates

    def get_home_coordinates(self):
        response = self.proxy.agent_status(agent_id=self.agent_id)
        data = json.loads(response.text)
        return data['agentData']['Scan']['Home'][0]

    def calculate_payload_distance(self, payload_coordinate):
        return abs(payload_coordinate[0]) + abs(payload_coordinate[1])

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

    def extract_payload_coordinates(self, response):
        data = json.loads(response.text)
        return data['agentData']['Scan']['Payloads']

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

class Action(Enum):
    TURN_LEFT = "turnLeft"
    TURN_RIGHT = "turnRight"
    MOVE_FORWARD = "moveForward"
    PICK_UP = "pickUp"
    DROP = "drop"
    IDLE = "idle"
    COMPLETE = "complete"
    AVOID_OBJECT = "avoid"


class AGENT_STATE(Enum):
    RETURN_HOME = 0
    SEARCH_HOME = 1
    RETRIEVE_PAYLOAD = 2
    SEARCH_PAYLOAD = 3
    AVOID_OBJECT = 4

class AVOID_STATE(Enum):
    TURN = 0
    MOVE = 1
    CORRECT = 2
    COMPLETE = 3

