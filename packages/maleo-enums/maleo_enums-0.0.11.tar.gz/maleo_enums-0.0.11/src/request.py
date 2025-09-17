from enum import StrEnum
from typing import List, Optional, Sequence


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


OptionalMethod = Optional[Method]
ListOfMethods = List[Method]
OptionalListOfMethods = Optional[ListOfMethods]
SequenceOfMethods = Sequence[Method]
OptionalSequenceOfMethods = Optional[SequenceOfMethods]


class Header(StrEnum):
    AUTHORIZATION = "authorization"
    CONTENT_TYPE = "content-type"
    X_API_KEY = "x-api-key"
    X_CLIENT_ID = "x-client-id"
    X_CLIENT_SECRET = "x-client-secret"
    X_NEW_AUTHORIZATION = "x-new-authorization"
    X_OPERATION_ID = "x-operation-id"
    X_ORGANIZATION_ID = "x-organization-id"
    X_PROCESS_TIME = "x-process-time"
    X_REQUEST_ID = "x-request-id"
    X_REQUESTED_AT = "x-requested-at"
    X_RESPONDED_AT = "x-responded-at"
    X_SIGNATURE = "x-signature"
    X_USER_ID = "x-user-id"


OptionalHeader = Optional[Header]
ListOfHeaders = List[Header]
OptionalListOfHeaders = Optional[ListOfHeaders]
SequenceOfHeaders = Sequence[Header]
OptionalSequenceOfHeaders = Optional[SequenceOfHeaders]
