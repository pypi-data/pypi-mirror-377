import csv
from typing import Annotated, Any

from pydantic import PlainSerializer, PlainValidator, StringConstraints, BeforeValidator


def _strip_space_after_dcid(v: Any) -> Any:
    if isinstance(v, str):
        if v.startswith("dcid:"):
            v = "dcid:" + v[5:].lstrip()
    return v


def _ensure_quoted(s: str) -> str:
    """Ensure a given string is enclosed in double quotes.

    Args:
        s: The input string to quote.

    Returns:
        A string enclosed in double quotes, stripped of leading/trailing whitespace.
    """
    if s.startswith("'") or s.startswith('"'):
        s = s.strip('"').strip("'").strip()
    return f'"{s}"'


def mcf_quoted_str(value: str | list[str] | None) -> str | None:
    """Serialise a string or list of strings to an MCF-compatible quoted string.

    Args:
        value: A string, list of strings, or None to serialise.

    Returns:
        An MCF-compatible quoted string or None if input is None.
    """
    if value is None:
        return None

    if isinstance(value, list):
        if len(value) < 2:
            return _ensure_quoted(value[0])

        return ",".join(_ensure_quoted(str(item)) for item in value)

    return _ensure_quoted(value)


def mcf_str(value: str | list[str] | None) -> str | None:
    """Serialise a string or list of strings without adding quotes.

    Args:
        value: A string, list of strings, or None to serialise.

    Returns:
        A comma-delimited string or None if input is None.
    """
    if value is None:
        return None

    if isinstance(value, list):
        if len(value) < 2:
            return str(value[0])

        return ", ".join(str(item) for item in value)

    return value


def parse_str_or_list(value: str | list[str]) -> str | list[str]:
    """Return a list when a comma-delimited string is provided."""
    if isinstance(value, str):
        parsed = next(csv.reader([value], skipinitialspace=True))
        parsed = [v.strip() for v in parsed]
        return parsed[0] if len(parsed) == 1 else parsed
    return value


QuotedStr = Annotated[
    str, PlainSerializer(_ensure_quoted, return_type=str | None, when_used="always")
]
"""A string annotated for serialisation into an MCF-compatible quoted format."""

QuotedStrListOrStr = Annotated[
    str | list[str],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_quoted_str, return_type=str | None, when_used="always"),
]
"""Accepts a string or list and serialises to quoted MCF format."""

StrOrListStr = Annotated[
    str | list[str],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_str, return_type=str | None, when_used="always"),
]
"""Accepts a string or list and serialises to a comma-separated string."""

Dcid = Annotated[
    str,
    BeforeValidator(_strip_space_after_dcid),
    StringConstraints(strip_whitespace=True, pattern=r"^dcid:\S+$"),
]

GroupDcid = Annotated[
    Dcid, StringConstraints(strip_whitespace=True, pattern=r"^dcid:.*g/.*")
]

PeerGroupDcid = Annotated[
    Dcid, StringConstraints(strip_whitespace=True, pattern=r"^dcid:.*svpg/.*")
]

TopicDcid = Annotated[
    Dcid, StringConstraints(strip_whitespace=True, pattern=r"^dcid:.*topic/.*")
]

DcidOrListDcid = Annotated[
    Dcid | list[Dcid],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_str, return_type=Dcid | None, when_used="always"),
]
"""Accepts a string or list and serialises to a comma-separated string."""


GroupDcidOrListGroupDcid = Annotated[
    GroupDcid | list[GroupDcid],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_str, return_type=GroupDcid | None, when_used="always"),
]
"""Accepts a string or list and serialises to a comma-separated string."""

PeerGroupDcidOrListPeerGroupDcid = Annotated[
    PeerGroupDcid | list[PeerGroupDcid],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_str, return_type=PeerGroupDcid | None, when_used="always"),
]
"""Accepts a string or list and serialises to a comma-separated string."""

TopicDcidOrListTopicDcid = Annotated[
    TopicDcid | list[TopicDcid],
    PlainValidator(parse_str_or_list),
    PlainSerializer(mcf_str, return_type=TopicDcid | None, when_used="always"),
]
"""Accepts a string or list and serialises to a comma-separated string."""
