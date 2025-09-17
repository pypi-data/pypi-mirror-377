from typing import Dict

from pydantic import BaseModel, HttpUrl, ConfigDict


class Source(BaseModel):
    """Representation of the Sources section of the config file

    Attributes:
        url: URL of the source.
        provenances: Dictionary of provenances. Each provenance name maps to a URL.
    """

    url: HttpUrl
    provenances: Dict[str, HttpUrl]  # Each provenance name maps to a URL

    model_config = ConfigDict(extra="forbid")
