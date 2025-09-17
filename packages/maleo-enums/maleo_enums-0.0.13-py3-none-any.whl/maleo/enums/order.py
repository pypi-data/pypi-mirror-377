from enum import StrEnum
from typing import List, Optional, Sequence


class Order(StrEnum):
    ASC = "asc"
    DESC = "desc"


OptionalOrder = Optional[Order]
ListOfOrders = List[Order]
OptionalListOfOrders = Optional[ListOfOrders]
SequenceOfOrders = Sequence[Order]
OptionalSequenceOfOrders = Optional[SequenceOfOrders]
