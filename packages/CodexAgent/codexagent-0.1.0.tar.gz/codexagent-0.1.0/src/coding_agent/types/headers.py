from pydantic import Field, BaseModel, AliasChoices


class WebhookHeaders(BaseModel):
    host: str = Field(
        default="",
        description="Request host (authority) header.",
        examples=["mtktma:8116"],
        validation_alias=AliasChoices("host"),
        serialization_alias="host",
        exclude=True,
    )
    user_agent: str = Field(
        default="",
        description="Client user agent identifier.",
        examples=["Go-http-client/1.1"],
        validation_alias=AliasChoices("user-agent"),
        serialization_alias="user-agent",
    )
    content_length: str = Field(
        default="",
        description="Length of request body in bytes.",
        examples=["76", "81"],
        validation_alias=AliasChoices("content-length"),
        serialization_alias="content-length",
        exclude=True,
    )
    content_type: str = Field(
        default="",
        description="Request payload media type.",
        examples=["application/json"],
        validation_alias=AliasChoices("content-type"),
        serialization_alias="content-type",
    )
