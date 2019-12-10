import json
from Agent import Agent
from enum import Enum


class OtherAgent(Agent):

    def __init__(self, proxy, agent_id):
        Agent.__init__(self, proxy, agent_id)

    def get_home_coordinates(self, response):
        data = json.loads(response.text)
        # if data['agentData']['Scan']['Home']:
        #    print(f" the actual home coordinates{tuple(data['agentData']['Scan']['Home'][0])}")
        #    print(f" the stored home coordinates{self.home_coordinates}")

        # if data['agentData']['Scan']['Home']:
        data = json.loads(response.text)
        return tuple(data['agentData']['Scan']['Home'][0])

    def get_all_coordinates(self, response):

        list = []

        data = json.loads(response.text)
        if data['agentData']['Scan']['Payloads']:
            payloads = data['agentData']['Scan']['Payloads']

            for payload in payloads:
                coordinate = Coordinate(payload[0], payload[1])
                #print(f'Payload: {coordinate.x}, {coordinate.y}')
                list.append(coordinate)

        if data['agentData']['Scan']['Home']:
            home = data['agentData']['Scan']['Home']

            for loc in home:
                coordinate = Coordinate(loc[0], loc[1])
                #print(f'Home: {coordinate.x}, {coordinate.y}')
                list.append(coordinate)

        if data['agentData']['Scan']['Agents']:
            agents = data['agentData']['Scan']['Agents']

            for agent in agents:
                coordinate = Coordinate(agent['Loc'][0], agent['Loc'][1])
                #print(f'Agents: {coordinate.x}, {coordinate.y}')
                list.append(coordinate)

        data = json.loads(response.text)
        if data['agentData']['Scan']['Walls']:
            walls = data['agentData']['Scan']['Walls']

            for wall in walls:
                x = 0
                y = 0
                if wall[0] == Wall.FRONT.value:
                    y = (wall[1] + 1)
                elif wall[0] == Wall.BACK.value:
                    y = (wall[1] + 1) * -1
                elif wall[0] == Wall.RIGHT.value:
                    x = (wall[1] + 1)
                elif wall[0] == Wall.LEFT.value:
                    x = (wall[1] + 1) * -1
                else:
                    print("Error: No wall found")

                coordinate = Coordinate(x, y)
                #print(f'Walls: {coordinate.x}, {coordinate.y}')
                list.append(coordinate)

        return list

    def get_wall_distance_list(self, response):
        dictionary = dict()
        data = json.loads(response.text)
        if data['agentData']['Scan']['Walls']:
            walls = data['agentData']['Scan']['Walls']

            for wall in walls:
                dictionary[wall[0]] = wall[1]
        #print(dictionary)
        return dictionary

    def get_max_scan_size(self, response):
        dictionary = self.get_wall_distance_list(response)
        #print(f'dictionary: {dictionary}')
        max = dict()
        max['W'] = 0
        max['H'] = 0
        if 'F' in dictionary and 'B' in dictionary:
            max['H'] = dictionary['F'] + dictionary['B']

        if 'L' in dictionary and 'R' in dictionary:
            max['W'] = dictionary['L'] + dictionary['R']

        if max['W'] == 0:
            max['W'] = max['H']

        if max['H'] == 0:
            max['H'] = max['W']

        return max

    def farthest_distance_dictionary(self, object_coordinates, response):
        dictionary = self.get_wall_distance_list(response)

        for coordinate in object_coordinates:
            if coordinate.y > 0 and ('F' not in dictionary or coordinate.x < dictionary['F']):
                dictionary['F'] = coordinate.y
            elif coordinate.y < 0 and ('B' not in dictionary or coordinate.y < dictionary['B']):
                dictionary['B'] = coordinate.y
            elif coordinate.x < 0 and ('L' not in dictionary or coordinate.x < dictionary['L']):
                dictionary['L'] = coordinate.x
            elif coordinate.x > 0 and ('R' not in dictionary or coordinate.x > dictionary['R']):
                dictionary['R'] = coordinate.x

        return dictionary

    def find_shortest_path(self, object_coordinates, response):
        target = Coordinate(1, 2)
        home = Coordinate(0, 0)
        visited = list()
        do_not_visit = list()
        visited.append(home)
        parent_of = dict()
        distance_to_coordidate = dict()
        parent_of[home] = home
        distance_to_coordidate[home] = 0
        locations = self.get_all_coordinates(response)
        dictionary = self.farthest_distance_dictionary(locations, response)
        max_scan = self.get_max_scan_size(response)

        while len(visited) != 0:
            current = visited.pop(0)
            print(f'current:{current.x}, {current.y}')
            # get all children
            if (current.y + 1) < max_scan['H']:
                top_coordinate = Coordinate(current.x, current.y + 1)
                if (not top_coordinate in object_coordinates and top_coordinate != home
                    and parent_of[current] != top_coordinate) \
                        or top_coordinate == target:
                    distance = distance_to_coordidate[current] + 1
                    if top_coordinate not in distance_to_coordidate or distance < distance_to_coordidate[
                        top_coordinate]:
                        distance_to_coordidate[top_coordinate] = distance
                        parent_of[top_coordinate] = current

                        if top_coordinate != target or top_coordinate not in do_not_visit:
                            visited.append(top_coordinate)
                            do_not_visit.append(top_coordinate)

            if (current.x + 1) < max_scan['W']:
                right_coordinate = Coordinate(current.x + 1, current.y)
                if not top_coordinate in object_coordinates and right_coordinate != home and parent_of[
                    current] != right_coordinate or right_coordinate == target:
                    distance = distance_to_coordidate[current] + 1
                    if right_coordinate not in distance_to_coordidate or distance < distance_to_coordidate[
                        right_coordinate]:
                        distance_to_coordidate[right_coordinate] = distance
                        parent_of[right_coordinate] = current

                        if right_coordinate != target or right_coordinate not in do_not_visit:
                            visited.append(right_coordinate)
                            do_not_visit.append(right_coordinate)

            if abs(current.x - 1) < max_scan['W']:
                left_coordinate = Coordinate(current.x - 1, current.y)
                if not left_coordinate in object_coordinates and left_coordinate != home and parent_of[
                    current] != left_coordinate or left_coordinate == target:
                    distance = distance_to_coordidate[current] + 1
                    if left_coordinate not in distance_to_coordidate or distance < distance_to_coordidate[
                        left_coordinate]:
                        distance_to_coordidate[left_coordinate] = distance
                        parent_of[left_coordinate] = current

                        if left_coordinate != target or left_coordinate not in do_not_visit:
                            visited.append(left_coordinate)
                            do_not_visit.append(left_coordinate)

            if abs(current.y - 1) < max_scan['W']:
                bottom_coordinate = Coordinate(current.x, current.y - 1)
                if not bottom_coordinate in object_coordinates and bottom_coordinate != home and \
                        parent_of[current] != bottom_coordinate or bottom_coordinate == target:
                    distance = distance_to_coordidate[current] + 1
                    if bottom_coordinate not in distance_to_coordidate or distance < distance_to_coordidate[
                        bottom_coordinate]:
                        distance_to_coordidate[bottom_coordinate] = distance
                        parent_of[bottom_coordinate] = current

                        if bottom_coordinate != target or bottom_coordinate not in do_not_visit:
                            visited.append(bottom_coordinate)
                            do_not_visit.append(bottom_coordinate)


'''function shortest_path_from (start)

  visited = new PriorityQueue
  visited.enqueue(start, 0)
  parent_of = new Hash
  parent_of[start] = nil # start vertex has no parent
  dist_to = new Hash
  dist_to[start] = 0 # start vertex's distance to itself is 0

  while visited priority queue is not empty
    current = visited.dequeue
    children = vertices that current is pointing at
    for each child in children
      dist = distance from current to child
      tent_dist = dist_to[current] + dist
      if child is not in dist_to or tent_dist < dist_to[child]
        dist_to[child] = tent_dist
        visited.enqueue(child, tent_dist)
        parent_of[child] = current
  return parent_of and dist_to'''


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Wall(Enum):
    FRONT = 'F'
    BACK = 'B'
    RIGHT = 'R'
    LEFT = 'L'
