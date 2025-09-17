from enum import StrEnum
from typing import List, Optional, Sequence


class DataStatus(StrEnum):
    DELETED = "deleted"
    INACTIVE = "inactive"
    ACTIVE = "active"


OptionalDataStatus = Optional[DataStatus]
ListOfDataStatuses = List[DataStatus]
OptionalListOfDataStatuses = Optional[ListOfDataStatuses]
SequenceOfDataStatuses = Sequence[DataStatus]
OptionalSequenceOfDataStatuses = Optional[SequenceOfDataStatuses]


FULL_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
    DataStatus.DELETED,
)

BASIC_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
)
