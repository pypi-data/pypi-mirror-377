from enum import StrEnum
from typing import List, Optional, Sequence


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


OptionalEnvironment = Optional[Environment]
ListOfEnvironments = List[Environment]
OptionalListOfEnvironments = Optional[ListOfEnvironments]
SequenceOfEnvironments = Sequence[Environment]
OptionalSequenceOfEnvironments = Optional[SequenceOfEnvironments]
