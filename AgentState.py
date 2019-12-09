from enum import Enum


class AgentState(Enum):
    RETURN_HOME = 0
    SEARCH_HOME = 1
    RETRIEVE_PAYLOAD = 2
    SEARCH_PAYLOAD = 3
    AVOID_OBJECT = 4
