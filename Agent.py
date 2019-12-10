import json
from Action import Action
from AgentState import AgentState
from AvoidState import AvoidState

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


class Agent:
    def __init__(self, proxy, agent_id):
        self.proxy = proxy
        self.agent_id = agent_id
        self.state = AgentState.SEARCH_PAYLOAD
        self.saved_state = AgentState.SEARCH_PAYLOAD
        self.avoid_state = AvoidState.CALCULATE
        self.saved_avoid_action = Action.IDLE
        self.home_coordinates = ()
        self.dropped_payload_coordinates = ()

    def do_stuff(self):

        response = self.proxy.agent_status(agent_id=self.agent_id)

        if self.state == AgentState.SEARCH_PAYLOAD:
            action = self.calculate_search_payload_action(response)
            if action == Action.COMPLETE:
                action = Action.IDLE
                self.state = AgentState.RETRIEVE_PAYLOAD
            elif action == Action.AVOID_OBJECT:
                action = action.IDLE
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.RETRIEVE_PAYLOAD:
            if not self.has_payload_coordinates(response):
                action = Action.IDLE
                self.state = AgentState.SEARCH_PAYLOAD
            else:
                coordinates = self.get_closest_payload_coordinates(response)
                action = self.calculate_action(response, coordinates)
                if action == Action.COMPLETE:
                    action = Action.PICK_UP
                    self.state = AgentState.SEARCH_HOME
                elif action == Action.AVOID_OBJECT:
                    action = action.IDLE
                    self.saved_state = self.state
                    self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.SEARCH_HOME:
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
            if action == Action.COMPLETE:
                action = Action.DROP
                self.state = AgentState.SEARCH_PAYLOAD
            elif action == Action.AVOID_OBJECT:
                action = action.IDLE
                self.saved_state = self.state
                self.state = AgentState.AVOID_OBJECT

        elif self.state == AgentState.AVOID_OBJECT:
            action = self.calculate_avoid_object_action(response)
            if action == Action.COMPLETE:
                action = action.IDLE
                self.state = self.saved_state

        #if self.has_home_coordinates(response):
            #self.update_home_coordinates(action)

        print(f"{self.agent_id}: {self.state}")
        print(f"{self.agent_id}: {action}")
        self.action(action)

    def update_home_coordinates(self, action):

        if action == Action.TURN_LEFT:
            print(f"Old Home Coordinates: {self.home_coordinates}")
            new_x_coordinate = abs(self.home_coordinates[Y_COORDINATE])
            new_y_coordinate = abs(self.home_coordinates[X_COORDINATE])
            if self.home_coordinates[X_COORDINATE] >= 0 and self.home_coordinates[Y_COORDINATE] > 0:
                new_x_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] < 0 and self.home_coordinates[Y_COORDINATE] > 0:
                new_y_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] <= 0 and self.home_coordinates[Y_COORDINATE] < 0:
                new_x_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] > 0 and self.home_coordinates[Y_COORDINATE] < 0:
                new_y_coordinate *= -1
            self.home_coordinates = (new_x_coordinate, new_y_coordinate)
        elif action == Action.TURN_RIGHT:
            print(f"Old Home Coordinates: {self.home_coordinates}")
            new_x_coordinate = abs(self.home_coordinates[Y_COORDINATE])
            new_y_coordinate = abs(self.home_coordinates[X_COORDINATE])
            if self.home_coordinates[X_COORDINATE] > 0 and self.home_coordinates[Y_COORDINATE] >= 0:
                new_y_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] > 0 and self.home_coordinates[Y_COORDINATE] < 0:
                new_x_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] < 0 and self.home_coordinates[Y_COORDINATE] <= 0:
                new_y_coordinate *= -1
            elif self.home_coordinates[X_COORDINATE] < 0 and self.home_coordinates[Y_COORDINATE] > 0:
                new_x_coordinate *= -1
            self.home_coordinates = (new_x_coordinate, new_y_coordinate)
        elif action == Action.MOVE_FORWARD:
            new_y_coordinate = self.home_coordinates[Y_COORDINATE] - 1
            new_x_coordinate = self.home_coordinates[X_COORDINATE]
            self.home_coordinates = (new_x_coordinate, new_y_coordinate)
        print(f"New Home Coordinates: {self.home_coordinates}")

    def update_last_dropped_package_coordinates(self, action):

        if action == Action.TURN_LEFT:
            print(f"Last Held Package Coordinates: {self.dropped_payload_coordinates}")
            new_x_coordinate = abs(self.dropped_payload_coordinates[Y_COORDINATE])
            new_y_coordinate = abs(self.dropped_payload_coordinates[X_COORDINATE])
            if self.dropped_payload_coordinates[X_COORDINATE] >= 0 and self.dropped_payload_coordinates[Y_COORDINATE] > 0:
                new_x_coordinate *= -1
            elif self.dropped_payload_coordinates[X_COORDINATE] < 0 and self.dropped_payload_coordinates[Y_COORDINATE] > 0:
                new_y_coordinate *= 1
                new_x_coordinate *= 1
            elif self.dropped_payload_coordinates[X_COORDINATE] <= 0 and self.dropped_payload_coordinates[Y_COORDINATE] < 0:
                new_x_coordinate *= -1
            elif self.dropped_payload_coordinates[X_COORDINATE] > 0 and self.dropped_payload_coordinates[Y_COORDINATE] < 0:
                new_y_coordinate *= -1
                new_x_coordinate *= -1
            self.dropped_payload_coordinates = (new_x_coordinate, new_y_coordinate)
        elif action == Action.TURN_RIGHT:
            print(f"Old Dropped Coordinates: {self.dropped_payload_coordinates}")
            new_x_coordinate = abs(self.dropped_payload_coordinates[Y_COORDINATE])
            new_y_coordinate = abs(self.dropped_payload_coordinates[X_COORDINATE])
            if self.dropped_payload_coordinates[X_COORDINATE] >= 0 and self.dropped_payload_coordinates[Y_COORDINATE] > 0:
                new_x_coordinate *= -1
            elif self.dropped_payload_coordinates[X_COORDINATE] > 0 and self.dropped_payload_coordinates[Y_COORDINATE] < 0:
                new_y_coordinate *= 1
                new_x_coordinate *= 1
            elif self.dropped_payload_coordinates[X_COORDINATE] <= 0 and self.dropped_payload_coordinates[Y_COORDINATE] < 0:
                new_x_coordinate *= -1
            elif self.dropped_payload_coordinates[X_COORDINATE] < 0 and self.dropped_payload_coordinates[Y_COORDINATE] > 0:
                new_y_coordinate *= -1
                new_x_coordinate *= -1
            self.dropped_payload_coordinates = (new_x_coordinate, new_y_coordinate)
        elif action == Action.MOVE_FORWARD:
            new_y_coordinate = self.dropped_payload_coordinates[Y_COORDINATE] - 1
            new_x_coordinate = self.dropped_payload_coordinates[X_COORDINATE]
            self.dropped_payload_coordinates = (new_x_coordinate, new_y_coordinate)
        print(f"New Dropped Coordinates: {self.dropped_payload_coordinates}")

    def has_payload(self, response):
        data = json.loads(response.text)
        return data['agentData']['Status']['Payload'] != 'None'

    def calculate_avoid_agent_action(self, response):

        return True

    def has_agent_collision(self, response):
        dictionary = self.create_agent_dictionary(response)
        if self.has_agent_at_coordinate(dictionary, DIRECTLY_IN_FRONT):
            return True
        else:
            return False

    def has_agent_at_coordinate(self, dictionary, location):

        if location in dictionary.keys():
            return True
        else:
            return False

    def create_agent_dictionary(self, response):
        data = json.loads(response.text)
        agents = data['agentData']['Scan']['Agents']
        dictionary = dict()
        for agent in agents:
            dictionary[tuple(agent['Loc'])] = agent

        return dictionary

    def get_agent_coordinates(self, response):
        data = json.loads(response.text)
        agents = data['agentData']['Scan']['Agents']
        agent_list = []
        for agent in agents:
            agent_list.append(agent['Loc'])

        return agent_list

    def has_agent_coordinates(self, response):
        data = json.loads(response.text)
        if data['agentData']['Scan']['Agents']:
            return True
        else:
            return False

    def calculate_avoid_object_action(self, response):

        if self.avoid_state == AvoidState.CALCULATE:
            self.calculate_avoid_action(response)
        if self.avoid_state == AvoidState.TURN:
            action = self.calculate_turn_action(response)
            self.avoid_state = AvoidState.CALCULATE
        elif self.avoid_state == AvoidState.MOVE:
            action = Action.MOVE_FORWARD
            self.avoid_state = AvoidState.CORRECT
        elif self.avoid_state == AvoidState.CORRECT:
            action = self.calculate_correct_action()
            self.avoid_state = AvoidState.COMPLETE
        elif self.avoid_state == AvoidState.COMPLETE:
            action = Action.COMPLETE
            self.avoid_state = AvoidState.CALCULATE
        else:
            action = Action.IDLE

        return action

    def calculate_avoid_action(self, response):
        if self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT):
            self.avoid_state = AvoidState.TURN
        else:
            self.avoid_state = AvoidState.MOVE



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
                self.saved_avoid_action = Action.TURN_RIGHT
        else:
            action = Action.IDLE
            self.saved_avoid_action = Action.IDLE

        '''elif self.has_possible_agent_collision(response):
            dictionary = self.create_agent_dictionary(response)
            action = Action.MOVE_FORWARD

            if self.has_agent_at_coordinate(dictionary, CORNER_LEFT):
                agent = dictionary[CORNER_LEFT]
                agent_status = self.read_mode(agent['Status'])
                if agent['Heading'] == 'R' and agent_status.agent_state == Action.MOVE_FORWARD and agent_status < self.agent_id:
                    action = Action.IDLE

            if self.has_agent_at_coordinate(dictionary, CORNER_RIGHT):
                agent = dictionary[CORNER_RIGHT]
                agent_status = self.read_mode(agent['Status'])
                if agent['Heading'] == 'L' and agent_status.agent_state == Action.MOVE_FORWARD and agent_status < self.agent_id:
                    action = Action.IDLE

            if self.has_agent_at_coordinate(dictionary, IN_FRONT):
                agent = dictionary[IN_FRONT]
                agent_status = self.read_mode(agent['Status'])
                if agent['Heading'] == 'B' and agent_status.agent_state == Action.MOVE_FORWARD and agent_status < self.agent_id:
                    action = Action.IDLE
        else:
            action = Action.MOVE_FORWARD
            # Agent Moved
            action = Action.MOVE_FORWARD'''

        return action

    def calculate_correct_action(self):
        if self.is_search_state() and self.saved_avoid_action == Action.TURN_LEFT:
            action = Action.TURN_RIGHT
        elif self.is_search_state() and self.saved_avoid_action == Action.TURN_RIGHT:
            action = Action.TURN_LEFT
        else:
            action = Action.IDLE

        #TODO: if left has wall in it and no payload over there, go straight or go right

        return action

    def is_search_state(self):
        return self.saved_state == AgentState.SEARCH_PAYLOAD or self.saved_state == AgentState.SEARCH_HOME

    def calculate_search_payload_action(self, response):

        if self.has_payload_coordinates(response):
            action = Action.COMPLETE
        elif self.has_wall_in_distance(response, 'F') and self.has_wall_in_distance(response, 'L'):
            action = Action.TURN_RIGHT
        elif self.has_wall_in_distance(response, 'F'):
            action = Action.TURN_LEFT
        else:
            action = Action.MOVE_FORWARD

        if action == Action.MOVE_FORWARD and self.has_possible_collision(response):
            action = Action.AVOID_OBJECT

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

        if action == Action.MOVE_FORWARD and self.has_possible_collision(response):
            action = Action.AVOID_OBJECT

        return action

    def calculate_payload_distance(self, coordinates):
        return abs(coordinates[0]) + abs(coordinates[1])

    def calculate_action(self, response, coordinates):
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
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] > 0:
            action = Action.MOVE_FORWARD
        else:
            action = Action.MOVE_FORWARD

        if action == Action.MOVE_FORWARD and self.has_possible_collision(response):
            action = Action.AVOID_OBJECT

        return action

    def calculate_return_home_action(self, response, coordinates):
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
        elif coordinates[X_COORDINATE] == 0 and coordinates[Y_COORDINATE] > 0:
            action = Action.MOVE_FORWARD
        else:
            action = Action.MOVE_FORWARD

        if action == Action.MOVE_FORWARD and self.has_possible_collision(response):
            action = Action.AVOID_OBJECT

        return action

    # need avoid agent state machine

    def convert_list(self, lists):
        dictionary = dict()
        for items in lists:
            dictionary[items[0]] = items[1]
        return dictionary

    def action(self, action):
        mode = self.write_mode(action)
        self.proxy.agent_action(agent_id=self.agent_id, action=action.action_value, mode=mode)

    def write_mode(self, action):
        mode = action.bit | (self.agent_id << 3)
        return mode

    def read_mode(self, mode):
        agent_state = mode & 7
        agent_id = mode >> 3 & 7
        agent_status = AgentStatus(agent_id = agent_id, agent_state=agent_state)
        return agent_status

    def get_closest_payload_coordinates(self, response):

        payloads_coordinates = self.get_payload_coordinates(response)

        if self.dropped_payload_coordinates in payloads_coordinates:
            payloads_coordinates.remove(self.dropped_payload_coordinates)

        closest_distance = -1

        for coordinates in payloads_coordinates:
            distance = self.calculate_payload_distance(coordinates)
            if closest_distance == -1:
                closest_distance = distance
                closest_coordinates = coordinates
            elif distance < closest_distance:
                closest_distance = distance
                closest_coordinates = coordinates

        return tuple(closest_coordinates)

    def get_payload_coordinates(self, response):
        data = json.loads(response.text)

        coordinate_list = list()
        coordinates = data['agentData']['Scan']['Payloads']

        for coordinate in coordinates:
            coordinate_list.append(tuple(coordinate))

        return coordinate_list

    def get_home_coordinates(self, response):
        data = json.loads(response.text)
        #if data['agentData']['Scan']['Home']:
        #    print(f" the actual home coordinates{tuple(data['agentData']['Scan']['Home'][0])}")
        #    print(f" the stored home coordinates{self.home_coordinates}")

        #if data['agentData']['Scan']['Home']:
        data = json.loads(response.text)
        return tuple(data['agentData']['Scan']['Home'][0])

        #return self.home_coordinates

    def has_payload_coordinates(self, response):
        data = json.loads(response.text)
        return data['agentData']['Scan']['Payloads']

    def has_new_payload_coordinates(self, response):
        data = json.loads(response.text)
        if data['agentData']['Scan']['Payloads']:
            coordinates = self.get_payload_coordinates(response)
            if self.dropped_payload_coordinates in coordinates:
                coordinates.remove(self.dropped_payload_coordinates)

            return coordinates
        else:
            return False

    def has_home_coordinates(self, response):

        data = json.loads(response.text)
        if data['agentData']['Scan']['Home']: #or self.home_coordinates:
            return True
        else:
            return False

    def has_wall_in_distance(self, response, direction):
        data = json.loads(response.text)
        wall_map = self.convert_list(data['agentData']['Scan']['Walls'])
        if direction not in wall_map or wall_map[direction] > AGENT_SCAN_DISTANCE:
            return False
        else:
            return True

    def has_possible_collision(self, response):

        # Finish this part later
        '''if self.has_possible_agent_collision(response):
            return True
        else:
            return self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT)'''

        has_object = self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT)
        return self.has_object_at_coordinate(response, DIRECTLY_IN_FRONT)

    def has_possible_agent_collision(self, response):
        dictionary = self.create_agent_dictionary(response)

        if self.has_agent_at_coordinate(dictionary, CORNER_LEFT):
            agent = dictionary[CORNER_LEFT]
            agent_status = self.read_mode(agent['Status'])

            if agent['Heading'] == 'R' and agent_status.agent_state == Action.MOVE_FORWARD:
                return True

        if self.has_agent_at_coordinate(dictionary, CORNER_RIGHT):
            agent = dictionary[CORNER_RIGHT]
            agent_status = self.read_mode(agent['Status'])

            if agent['Heading'] == 'L' and agent_status.agent_state == Action.MOVE_FORWARD:
                return True

        if self.has_agent_at_coordinate(dictionary, IN_FRONT):
            agent = dictionary[IN_FRONT]
            agent_status = self.read_mode(agent['Status'])

            if agent['Heading'] == 'B' and agent_status.agent_state == Action.MOVE_FORWARD:
                return True

    def has_object_at_coordinate(self, response, coordinate):

        dictionary = self.create_agent_dictionary(response)

        # get home
        if self.has_home_at_coordinates(response, coordinate):
            return True
        # get payload
        elif self.has_payload_at_coordininate(response, coordinate):
            return True
        elif self.has_agent_at_coordinate(dictionary, coordinate):
            return True
        else:
            return False
        # agent

    def has_home_at_coordinates(self, response, coordinate):
        if self.has_home_coordinates(response):
            home_coordinates = self.get_home_coordinates(response)
            if coordinate == home_coordinates:
                return True

    def has_payload_at_coordininate(self, response, coordinate):
        if self.has_payload_coordinates(response):
            payload_coordinates = self.get_payload_coordinates(response)
            return coordinate in payload_coordinates

    def test_3_test_1(self):
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

    def test_3_test_2(self):
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

    def test_3_test_4(self):
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_LEFT)
        self.test_move(Action.MOVE_FORWARD)
        self.test_move(Action.TURN_RIGHT)
        self.test_move(Action.MOVE_FORWARD)

    def test_move(self, action):
        self.action(action=action)
        self.proxy.step()


class AgentStatus:
    def __init__(self, agent_id, agent_state):
        self.agent_id = agent_id
        self.agent_state = agent_state
