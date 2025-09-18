from typing import Optional

from pydantic import Field, SecretStr

from prefect.blocks.core import Block


class Northflank(Block):
    """
    Northflank API credentials block for authenticating with the Northflank API.
    """

    api_token: Optional[SecretStr] = Field(
        default=None, description="Northflank API token for authentication"
    )
    base_url: str = Field(
        default="https://api.northflank.com",
        description="Base URL for the Northflank API",
    )
