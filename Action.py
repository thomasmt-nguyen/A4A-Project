from enum import Enum

class Action(Enum):

    TURN_LEFT = ("turnLeft", 0)
    TURN_RIGHT = ("turnRight", 1)
    MOVE_FORWARD = ("moveForward", 2)
    PICK_UP = ("pickUp", 3)
    DROP = ("drop", 4)
    IDLE = ("idle", 5)
    COMPLETE = ("complete", 6)
    AVOID_OBJECT = ("avoid", 7)

    def __init__(self, action_value, bit):
        self.action_value = action_value
        self.bit = bit

