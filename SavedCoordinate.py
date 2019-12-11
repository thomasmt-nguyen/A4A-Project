
from Action import Action

class SavedCoordinate():
    def __init__(self, coordinate, name):
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.name = name

    def update(self, action):
        if action == Action.TURN_LEFT:
            new_x_coordinate = abs(self.y)
            new_y_coordinate = abs(self.x)
            if self.x > 0 and self.y >= 0:
                new_y_coordinate *= -1
            elif self.x <= 0 and self.y > 0:
                new_y_coordinate *= 1
                new_x_coordinate *= 1
            elif self.x < 0 and self.y <= 0:
                new_x_coordinate *= -1
            elif self.x >= 0 and self.y < 0:
                new_y_coordinate *= -1
                new_x_coordinate *= -1
            else:
                print("Error: No rotation")
            self.x = new_x_coordinate
            self.y = new_y_coordinate

        elif action == Action.TURN_RIGHT:
            new_x_coordinate = abs(self.y)
            new_y_coordinate = abs(self.x)
            if self.x >= 0 and self.y > 0:
                new_x_coordinate *= -1
            elif self.x > 0 and self.y <= 0:
                new_y_coordinate *= 1
                new_x_coordinate *= 1
            elif self.x <= 0 and self.y < 0:
                new_y_coordinate *= -1
            elif self.x < 0 and self.y >= 0:
                new_y_coordinate *= -1
                new_x_coordinate *= -1
            else:
                print("Error: No rotation")

            self.x = new_x_coordinate
            self.y = new_y_coordinate

        elif action == Action.MOVE_FORWARD:
            new_y_coordinate = self.y - 1
            new_x_coordinate = self.x
            self.x = new_x_coordinate
            self.y = new_y_coordinate

class Coordinate:
    def __init__(self, x, y):
        self.x = x, self.y = y