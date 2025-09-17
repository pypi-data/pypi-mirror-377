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
    # --- Authentication & Authorization ---
    AUTHORIZATION = "authorization"
    PROXY_AUTHORIZATION = "proxy-authorization"
    WWW_AUTHENTICATE = "www-authenticate"

    # --- Content & Caching ---
    CACHE_CONTROL = "cache-control"
    CONTENT_DISPOSITION = "content-disposition"
    CONTENT_ENCODING = "content-encoding"
    CONTENT_LENGTH = "content-length"
    CONTENT_TYPE = "content-type"
    ETAG = "etag"
    LAST_MODIFIED = "last-modified"

    # --- Client & Request Context ---
    ACCEPT = "accept"
    ACCEPT_ENCODING = "accept-encoding"
    ACCEPT_LANGUAGE = "accept-language"
    HOST = "host"
    ORIGIN = "origin"
    REFERER = "referer"
    USER_AGENT = "user-agent"

    # --- Correlation / Observability ---
    X_OPERATION_ID = "x-operation-id"
    X_PROCESS_TIME = "x-process-time"
    X_REQUEST_ID = "x-request-id"
    X_REQUESTED_AT = "x-requested-at"
    X_RESPONDED_AT = "x-responded-at"
    X_TRACE_ID = "x-trace-id"
    X_SPAN_ID = "x-span-id"

    # --- Organization / User Context ---
    X_ORGANIZATION_ID = "x-organization-id"
    X_USER_ID = "x-user-id"

    # --- API Keys / Clients ---
    X_API_KEY = "x-api-key"
    X_CLIENT_ID = "x-client-id"
    X_CLIENT_SECRET = "x-client-secret"
    X_SIGNATURE = "x-signature"

    # --- Experimental / Misc ---
    X_FORWARDED_FOR = "x-forwarded-for"
    X_NEW_AUTHORIZATION = "x-new-authorization"
    X_REAL_IP = "x-real-ip"


OptionalHeader = Optional[Header]
ListOfHeaders = List[Header]
OptionalListOfHeaders = Optional[ListOfHeaders]
SequenceOfHeaders = Sequence[Header]
OptionalSequenceOfHeaders = Optional[SequenceOfHeaders]
