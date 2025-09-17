from typing import List

from pydantic import BaseModel
from .types import RxNormPropertyCategory, RxNormPropertyName


class SearchCandidate(BaseModel):
    rxcui: str
    rxaui: str
    score: str
    rank: str
    name: str | None = None
    source: str


class RelatedConcept(BaseModel):
    rxcui: int
    name: str
    synonym: str | None = None
    tty: str
    language: str | None = None
    suppress: str | None = None
    umlscui: str | None = None
    psn: str | None = None
    genCard: str | None = None


class RelatedGroup(BaseModel):
    tty: str
    concepts: List[RelatedConcept] = []


class FilterByPropertyResponse(BaseModel):
    """Response from filterByProperty API endpoint.

    See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.filterByProperty.html
    """

    rxcui: str | None = None


class NDCInfo(BaseModel):
    """Individual NDC information in findRelatedNDCs response."""

    ndc11: str | None = None
    status: str | None = None
    rxcui: str | None = None
    conceptName: str | None = None
    conceptStatus: str | None = None
    tty: str | None = None


class NDCInfoList(BaseModel):
    """Container for NDC info array."""
    ndcInfo: List[NDCInfo] = []


class FindRelatedNDCsResponse(BaseModel):
    """Response from findRelatedNDCs API endpoint.

    Returns list of NDCs related by product or concept.

    See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRelatedNDCs.html
    """

    ndcInfoList: NDCInfoList = NDCInfoList()


class IdGroup(BaseModel):
    """ID group containing RxNorm concept identifiers."""

    rxnormId: List[str] = []


class FindRxcuiByIdResponse(BaseModel):
    """Response from findRxcuiById and findRxcuiByString API endpoints.

    Returns RxCUIs associated with a specific identifier or name.
    Both endpoints use the same response format.

    See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiById.html
    See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiByString.html
    """

    idGroup: IdGroup | None = None


# Alias for clarity - both endpoints use the same response structure
FindRxcuiByStringResponse = FindRxcuiByIdResponse


class MinConcept(BaseModel):
    """Minimal concept information."""

    rxcui: str
    name: str
    tty: str


class MinConceptGroup(BaseModel):
    """Group containing minimal concepts."""

    minConcept: List[MinConcept] = []


class NDCTime(BaseModel):
    """NDC association time period."""

    ndc: List[str] = []
    startDate: str | None = None
    endDate: str | None = None


class HistoricalNDCTime(BaseModel):
    """Historical NDC time association."""

    status: str | None = None
    rxcui: str | None = None
    ndcTime: List[NDCTime] = []


class PropConcept(BaseModel):
    """Property concept with category, name, and value."""

    propCategory: RxNormPropertyCategory | None = None
    propName: RxNormPropertyName | None = None
    propValue: str | None = None


class PropertyConcept(BaseModel):
    """Individual property with name and value."""

    propName: str | None = None
    propValue: str | None = None


class NDCProperty(BaseModel):
    """NDC property details."""

    ndcItem: str | None = None
    ndc9: str | None = None
    ndc10: str | None = None
    rxcui: str | None = None
    splSetIdItem: str | None = None
    packagingList: List[str] = []
    propertyConceptList: List[PropertyConcept] = []
    source: str | None = None

    def __init__(self, **data):
        if 'packagingList' in data:
            packaging = data['packagingList']['packaging'] if isinstance(data['packagingList'], dict) else data['packagingList']
            data['packagingList'] = packaging

        if 'propertyConceptList' in data:
            property_concept = data['propertyConceptList']['propertyConcept'] if isinstance(data['propertyConceptList'], dict) else data['propertyConceptList']
            data['propertyConceptList'] = property_concept
        super().__init__(**data)


class SourceList(BaseModel):
    """List of source names."""

    sourceName: List[str] = []


class NDCSourceMapping(BaseModel):
    """NDC source mapping information."""

    ndcSource: str | None = None
    ndcActive: str | None = None
    ndcRxcui: str | None = None
    ndcConceptName: str | None = None
    ndcConceptStatus: str | None = None


class NDCHistory(BaseModel):
    """NDC history information."""

    activeRxcui: str | None = None
    originalRxcui: str | None = None
    startDate: str | None = None
    endDate: str | None = None


class NDCStatus(BaseModel):
    """NDC status information."""

    ndc11: str | None = None
    status: str | None = None
    active: str | None = None
    rxnormNdc: str | None = None
    rxcui: str | None = None
    conceptName: str | None = None
    conceptStatus: str | None = None
    sourceList: SourceList | None = None
    altNdc: str | None = None
    ndcSourceMapping: List[NDCSourceMapping] = []
    ndcHistory: List[NDCHistory] = []


class ProprietaryInfo(BaseModel):
    """Proprietary information from source vocabularies."""

    rxcui: str | None = None
    name: str | None = None
    type: str | None = None
    id: str | None = None
    source: str | None = None


class ProprietaryGroup(BaseModel):
    """Group containing proprietary information."""

    proprietaryInfo: List[ProprietaryInfo] = []


class ReformulationConcept(BaseModel):
    """Reformulation concept pair showing original and new formulation."""

    rxcui: str | None = None
    reformulatedRxcui: str | None = None
    name: str | None = None
    reformulatedName: str | None = None


class RelationPath(BaseModel):
    """Relationship path showing traversal between term types."""

    tty: List[str] = []


class RxNormVersionInfo(BaseModel):
    """RxNorm version information."""

    version: str | None = None
    apiVersion: str | None = None
