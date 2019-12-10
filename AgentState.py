from enum import Enum


class AgentState(Enum):
    RETURN_HOME = 0
    SEARCH_HOME = 1
    RETRIEVE_PAYLOAD = 2
    SEARCH_PAYLOAD = 3
    WAIT_FOR_PAYLOAD = 4
    SEARCH_AGENT = 5
    MOVE_TO_AGENT = 6
    AVOID_OBJECT = 7
