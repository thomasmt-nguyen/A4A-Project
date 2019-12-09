from enum import Enum


class AvoidState(Enum):
    TURN = 0
    MOVE = 1
    CORRECT = 2
    COMPLETE = 3