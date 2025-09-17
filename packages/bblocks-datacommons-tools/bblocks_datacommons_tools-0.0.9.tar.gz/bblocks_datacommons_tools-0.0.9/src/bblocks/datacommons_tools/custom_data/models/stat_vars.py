from enum import StrEnum
from typing import Optional, List, Dict, Literal

from pydantic import BaseModel, ConfigDict, constr


from bblocks.datacommons_tools.custom_data.models.common import (
    QuotedStrListOrStr,
    StrOrListStr,
    Dcid,
    GroupDcid,
    PeerGroupDcid,
    DcidOrListDcid,
    GroupDcidOrListGroupDcid,
)

from bblocks.datacommons_tools.custom_data.models.mcf import MCFNode


class StatType(StrEnum):
    """Enumeration of statistical value types used in Data Commons."""

    MEASURED_VALUE = "dcid:measuredValue"
    MIN_VALUE = "dcid:minValue"
    MAX_VALUE = "dcid:maxValue"
    MEAN_VALUE = "dcid:meanValue"
    MEDIAN_VALUE = "dcid:medianValue"
    SUM_VALUE = "dcid:sumValue"
    VARIANCE_VALUE = "dcid:varianceValue"
    MARGIN_OF_ERROR = "dcid:marginOfError"
    STANDARD_ERROR = "dcid:stdErr"


class Variable(BaseModel):
    """Representation of the Variables section of the config file
    This section is optional in the config file

    Attributes:
        name: Name of the variable.
        description: Description of the variable.
        searchDescriptions: List of search descriptions for the variable.
        group: Group to which the variable belongs.
        properties: Properties of the variable.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    searchDescriptions: Optional[List[str]] = None
    group: Optional[StrOrListStr] = None
    properties: Optional[Dict[str, str]] = None

    model_config = ConfigDict(extra="forbid")


class StatVarMCFNode(MCFNode):
    """Represents a Statistical Variable node in MCF.

    Attributes:
        # Inherited from MCFNode
        Node: Identifier for the Node.
        name: The human-readable name for the Node.
        dcid: Optional DCID for uniquely identifying the Node.
        description: Optional human-readable description.
        provenance: Optional provenance information.
        shortDisplayName: Optional human-readable short name for display.
        subClassOf: Optional DCID indicating the 'parent' Node class.

        # Additional Attributes specific to StatisticalVariable
        statType: Type of statistical measurement represented by the variable.
        typeOf: Fixed type indicating this is a StatisticalVariable.
        memberOf: Optional DCID indicating group membership.
        relevantVariable: Optional DCID of a related variable.
        searchDescription: Optional descriptions enhancing NL search capabilities.
        populationType: Optional DCID of the population entity type being measured.
        measuredProperty: Optional DCID of the property being measured.
        measurementQualifier: Optional qualifier describing measurement specifics.
        measurementDenominator: Optional denominator for ratio-type statistical measures.
        footnote: Optional footnotes providing additional context or information.
    """

    statType: Optional[StatType] = StatType.MEASURED_VALUE
    typeOf: Literal["dcid:StatisticalVariable"] = "dcid:StatisticalVariable"
    memberOf: Optional[GroupDcidOrListGroupDcid] = None
    relevantVariable: Optional[DcidOrListDcid] = None
    searchDescription: Optional[QuotedStrListOrStr] = None
    populationType: Optional[Dcid] = None
    measuredProperty: Optional[Dcid] = None
    measurementQualifier: Optional[Dcid] = None
    measurementDenominator: Optional[Dcid] = None
    footnote: Optional[QuotedStrListOrStr] = None


class StatVarGroupMCFNode(MCFNode):
    """Represents a Statistical Variable Group node in MCF.

    Attributes:
        # Additional Attributes specific to StatVarGroup
        Node: Node identifier, must contain '/g'.
        typeOf: Fixed type indicating this is a StatVarGroup.
        specializationOf: DCID of the parent group, must start with 'dcid:' and contain 'g/'.

         # Inherits from MCFNode
        name: The human-readable name for the Node.
        dcid: Optional DCID for uniquely identifying the Node.
        description: Optional human-readable description.
        provenance: Optional provenance information.
        shortDisplayName: Optional human-readable short name for display.
        subClassOf: Optional DCID indicating the 'parent' Node class.
    """

    Node: GroupDcid
    typeOf: Literal["dcid:StatVarGroup"] = "dcid:StatVarGroup"
    specializationOf: GroupDcid


class StatVarPeerGroupMCFNode(MCFNode):
    """Represents a Statistical Variable Peer Group node in MCF.
    A StatVarPeerGroup represents a group of StatisticalVariable nodes that are comparable peers.

    Attributes:
        # Additional Attributes specific to StatVarPeerGroup
        Node: Node identifier, must contain '/svpg'.
        typeOf: Fixed type indicating this is a StatVarPeerGroup.
        member: DCID of the parent group, must start with 'dcid:' and contain 'g/'.

         # Inherits from MCFNode
        name: The human-readable name for the Node.
        dcid: Optional DCID for uniquely identifying the Node.
        description: Optional human-readable description.
        provenance: Optional provenance information.
        shortDisplayName: Optional human-readable short name for display.
        subClassOf: Optional DCID indicating the 'parent' Node class.
    """

    Node: PeerGroupDcid
    typeOf: Literal["dcid:StatVarPeerGroup"] = "dcid:StatVarPeerGroup"
    member: DcidOrListDcid
