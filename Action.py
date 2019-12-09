from enum import Enum


class Action(Enum):
    TURN_LEFT = "turnLeft"
    TURN_RIGHT = "turnRight"
    MOVE_FORWARD = "moveForward"
    PICK_UP = "pickUp"
    DROP = "drop"
    IDLE = "idle"
    COMPLETE = "complete"
    AVOID_OBJECT = "avoid"
