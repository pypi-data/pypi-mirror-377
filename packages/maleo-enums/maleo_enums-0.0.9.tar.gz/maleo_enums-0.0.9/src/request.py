from enum import StrEnum


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class Header(StrEnum):
    AUTHORIZATION = "authorization"
    CONTENT_TYPE = "content-type"
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
