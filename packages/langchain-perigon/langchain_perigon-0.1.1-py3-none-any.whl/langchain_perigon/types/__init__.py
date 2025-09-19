from typing import List, Optional, TypedDict, Union


class Coordinates(TypedDict, total=False):
    lat: float
    lon: float
    radius: float


class RagFilter(TypedDict, total=False):
    articleId: Optional[Union[str, List[str]]]
    clusterId: Optional[Union[str, List[str]]]
    source: Optional[Union[str, List[str]]]
    sourceGroup: Optional[Union[str, List[str]]]
    language: Optional[Union[str, List[str]]]
    label: Optional[Union[str, List[str]]]
    category: Optional[Union[str, List[str]]]
    topic: Optional[Union[str, List[str]]]
    country: Optional[Union[str, List[str]]]
    locationsCountry: Optional[Union[str, List[str]]]
    state: Optional[Union[str, List[str]]]
    county: Optional[Union[str, List[str]]]
    city: Optional[Union[str, List[str]]]
    coordinates: Optional[Coordinates]
    sourceCountry: Optional[Union[str, List[str]]]
    sourceState: Optional[Union[str, List[str]]]
    sourceCounty: Optional[Union[str, List[str]]]
    sourceCity: Optional[Union[str, List[str]]]
    sourceCoordinates: Optional[Coordinates]
    companyId: Optional[Union[str, List[str]]]
    companyDomain: Optional[Union[str, List[str]]]
    companySymbol: Optional[Union[str, List[str]]]
    companyName: Optional[Union[str, List[str]]]
    personWikidataId: Optional[Union[str, List[str]]]
    personName: Optional[Union[str, List[str]]]
    AND: Optional[List["RagFilter"]]
    OR: Optional[List["RagFilter"]]
    NOT: Optional[Union["RagFilter", List["RagFilter"]]]


class ArticlesFilter(TypedDict, total=False):
    size: Optional[int]
    showReprints: Optional[bool]
    filter: Optional[RagFilter]


class WikipediaFilter(TypedDict, total=False):
    wikidataId: Optional[Union[str, List[str]]]
    wikidataInstanceOfId: Optional[Union[str, List[str]]]
    wikidataInstanceOfLabel: Optional[Union[str, List[str]]]
    wikiCode: Optional[Union[str, List[str]]]
    category: Optional[Union[str, List[str]]]
    title: Optional[str]
    summary: Optional[str]
    text: Optional[str]
    reference: Optional[str]
    withPageviews: Optional[bool]
    AND: Optional[List["WikipediaFilter"]]
    OR: Optional[List["WikipediaFilter"]]
    NOT: Optional[Union["WikipediaFilter", List["WikipediaFilter"]]]


class WikipediaOptions(TypedDict, total=False):
    size: Optional[int]
    page: Optional[int]
    pageviewsFrom: Optional[int]
    pageviewsTo: Optional[int]
    wikiRevisionFrom: Optional[str]
    wikiRevisionTo: Optional[str]
    filter: Optional[WikipediaFilter]
