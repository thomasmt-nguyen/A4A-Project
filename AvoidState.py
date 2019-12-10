from enum import Enum


class AvoidState(Enum):
    CALCULATE = 0
    TURN = 1
    MOVE = 2
    CORRECT = 3
    WAIT = 4
    COMPLETE = 5
