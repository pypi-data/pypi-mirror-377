"""
Predefined errors that the product gateway or data sources can return.

These errors can not be overridden by the data product definition itself.
"""

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr


class BaseApiError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    __status__: int

    @classmethod
    def get_response_spec(cls):
        return {"model": cls}


class ApiError(BaseApiError):
    type: StrictStr = Field(
        ...,
        title="Error type",
        description="Error identifier",
    )
    message: StrictStr = Field(
        ...,
        title="Error message",
        description="Error description",
    )


class ApiOrExternalError(BaseApiError):
    @classmethod
    def get_response_spec(cls):
        return {"model": cls, "content": {"text/plain": {}, "text/html": {}}}


class Unauthorized(ApiError):
    __status__ = 401


class Forbidden(ApiError):
    __status__ = 403


class NotFound(ApiError):
    __status__ = 404


# Note: 422 is added automatically by FastAPI


class RateLimitExceeded(BaseApiError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 429
    message: StrictStr = Field(
        "Rate limit exceeded",
        title="Error message",
        description="Error description",
    )


class DataSourceNotFound(BaseApiError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 444
    message: StrictStr = Field(
        "Data source not found",
        title="Error message",
        description="Error description",
    )


class DataSourceError(ApiError):
    __status__ = 500


class BadGateway(BaseApiError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 502


class ServiceUnavailable(ApiOrExternalError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 503
    message: StrictStr = Field(
        "",
        title="Error message",
        description="Error description",
    )


class GatewayTimeout(ApiOrExternalError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 504
    message: StrictStr = Field(
        "",
        title="Error message",
        description="Error description",
    )


class DoesNotConformToDefinition(BaseApiError):
    """
    This response is reserved by Product Gateway.
    """

    __status__ = 550
    message: StrictStr = "Response from data source does not conform to definition"
    data_source_status_code: StrictInt = Field(
        ...,
        title="Data source status code",
        description="HTTP status code returned from the data source",
    )


DATA_PRODUCT_ERRORS = {
    resp.__status__: resp.get_response_spec()
    for resp in [
        Unauthorized,
        Forbidden,
        NotFound,
        RateLimitExceeded,
        DataSourceNotFound,
        DataSourceError,
        BadGateway,
        ServiceUnavailable,
        GatewayTimeout,
        DoesNotConformToDefinition,
    ]
}
