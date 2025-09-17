from datetime import timedelta

from .shared import _BaseOptionEnum, _parse_str, _parse_bool, _parse_enum, _parse_positive_int

class AuthMethod(_BaseOptionEnum):
    """
    Enum for the authentication methods supported by the Pi Web API.
    """
    ANONYMOUS = "anonymous"
    BASIC = "basic"
    KERBEROS = "kerberos"
    BEARER = "bearer"

class RowLevelErrorHandling(_BaseOptionEnum):
    """
    Enum for the row-level error handling strategies for row-level errors.
    """
    RAISE = "raise"
    EXCLUDE = "exclude"
    NULLIFY = "nullify"

class PiDataSourceConfig:
    host: str
    auth_method: AuthMethod
    username: str | None
    password: str | None
    token: str | None
    verify: bool
    server: str | None
    rate_limit_duration: timedelta
    rate_limit_max_requests: int
    max_returned_items_per_call: int
    row_level_error_handling: RowLevelErrorHandling

    def __init__(self, options: dict[str, str]) -> None:
        self.host = _parse_str(options, "host", required=True).rstrip('/')
        self.auth_method = _parse_enum(options, "authMethod", AuthMethod, default="anonymous")
        self.username = _parse_str(options, "username", required=self.auth_method == AuthMethod.BASIC)
        self.password = _parse_str(options, "password", required=self.auth_method == AuthMethod.BASIC)
        self.token = _parse_str(options, "token", required=self.auth_method == AuthMethod.BEARER)
        self.verify = _parse_bool(options, "verify", default="true")
        self.server = _parse_str(options, "server")
        self.rate_limit_duration = timedelta(seconds=_parse_positive_int(options, "rateLimitDuration", default="1")) # In the actual Pi server config, this is specified as a number of seconds, not an AFTimeSpan string.
        self.rate_limit_max_requests = _parse_positive_int(options, "rateLimitMaxRequests", default="1000")
        self.max_returned_items_per_call = _parse_positive_int(options, "maxReturnedItemsPerCall", default="150000")
        self.row_level_error_handling = _parse_enum(options, "rowLevelErrorHandling", RowLevelErrorHandling, default="raise")
