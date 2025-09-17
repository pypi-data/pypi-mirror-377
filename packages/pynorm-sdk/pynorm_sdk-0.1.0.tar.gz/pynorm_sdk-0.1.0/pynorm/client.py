from datetime import datetime
from typing import Any, Dict, Optional, List, Literal, Type, TypeVar
import asyncio
import aiohttp
import logging
from pydantic import BaseModel, ValidationError

from .exceptions import (
    RxNormConnectionError,
    RxNormHTTPError,
    RxNormNotFoundError,
    RxNormParsingError,
    RxNormServerError,
    RxNormSessionError,
    RxNormTimeoutError,
)
from .models import (
    FilterByPropertyResponse,
    FindRelatedNDCsResponse,
    FindRxcuiByIdResponse,
    FindRxcuiByStringResponse,
    HistoricalNDCTime,
    MinConcept,
    NDCProperty,
    NDCStatus,
    PropConcept,
    ProprietaryInfo,
    ReformulationConcept,
    RelatedConcept,
    RelatedGroup,
    RelationPath,
    RxNormVersionInfo,
    SearchCandidate,
)
from .types import (
    RxNormIdType,
    RxNormPropertyCategory,
    RxNormPropertyName,
    RxNormRelationshipType,
    RxNormSourceType,
    RxNormTermType,
)

BASE_API_URL = "https://rxnav.nlm.nih.gov/REST"

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class RxNormClient:
    """Async client for the RxNorm API.
    
    Provides methods to interact with the RxNorm REST API for drug information.
    Can be used as a context manager for automatic session lifecycle management
    or with an injected session for custom configuration.
    
    Example:
        # As context manager
        async with RxNormClient() as client:
            result = await client.some_method()
            
        # With injected session
        async with aiohttp.ClientSession() as session:
            client = RxNormClient(session=session)
            result = await client.some_method()
    """

    def __init__(
        self, 
        session: Optional[aiohttp.ClientSession] = None,
        base_url: str = BASE_API_URL
    ):
        """Initialize RxNorm client.
        
        Args:
            session: Optional aiohttp session. If None, one will be created
                    when used as context manager.
            base_url: Base URL for RxNorm API. Defaults to official endpoint.
        """
        self._session = session
        self._base_url = base_url.rstrip('/')
        self._owns_session = session is None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the HTTP session, raising error if not initialized."""
        if self._session is None:
            raise RxNormSessionError(
                "RxNormClient session is not initialized. "
                "Use as context manager or provide a session."
            )
        return self._session

    async def __aenter__(self) -> "RxNormClient":
        """Enter async context manager, creating session if needed."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "py-norm/0.1.0"
                }
            )
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exit async context manager, closing session if we own it."""
        if self._session and self._owns_session:
            await self._session.close()
            self._session = None

    async def _make_api_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to RxNorm API.
        
        Args:
            endpoint: API endpoint path (without .json suffix)
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            RxNormConnectionError: For network connectivity issues
            RxNormHTTPError: For HTTP status errors
            RxNormParsingError: For JSON parsing errors
        """
        url = f"{self._base_url}/{endpoint}.json"
        request_params = params or {}
        
        logger.debug(f"Making request to {url} with params: {request_params}")
        
        try:
            async with self.session.get(url, params=request_params) as response:
                # Handle HTTP errors with specific exceptions
                if response.status == 404:
                    raise RxNormNotFoundError(f"Endpoint not found: {url}")
                elif response.status >= 500:
                    raise RxNormServerError(
                        f"Server error {response.status}: {response.reason}",
                        response.status
                    )
                elif response.status >= 400:
                    raise RxNormHTTPError(
                        f"HTTP error {response.status}: {response.reason}",
                        response.status
                    )
                
                try:
                    return await response.json()
                except (ValueError, aiohttp.ContentTypeError) as e:
                    raw_text = await response.text()
                    raise RxNormParsingError(f"Failed to parse JSON response: {e}", raw_text)
                    
        except asyncio.TimeoutError as e:
            logger.error(f"Request to {url} timed out: {e}")
            raise RxNormTimeoutError(f"Request timed out: {url}")
        except aiohttp.ServerTimeoutError as e:
            logger.error(f"Server timeout for {url}: {e}")
            raise RxNormTimeoutError(f"Server timeout: {url}")
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection failed to {url}: {e}")
            raise RxNormConnectionError(f"Failed to connect to RxNorm API: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"Request to {url} failed: {e}")
            raise RxNormConnectionError(f"Request failed: {e}")

    def _extract_list_from_response(
        self, 
        response: Dict[str, Any], 
        path: List[str], 
        model_class: Type[T]
    ) -> List[T]:
        """Helper to extract and validate lists from nested API responses.
        
        Args:
            response: The API response dictionary
            path: List of keys to traverse (e.g., ["brandGroup", "conceptProperties"])
            model_class: Pydantic model class to validate each item
            
        Returns:
            List of validated model instances
        """
        current = response
        for key in path:
            current = current.get(key)
            if not current:
                return []
        
        if not isinstance(current, list):
            return []
            
        validated_items = []
        for item in current:
            if not item or not isinstance(item, dict):
                continue
            try:
                validated_items.append(model_class.model_validate(item))
            except ValidationError as e:
                logger.warning(f"Failed to validate {model_class.__name__}: {e}")
                # Skip invalid items rather than failing entire request
                continue
                
        return validated_items

    def _extract_single_from_response(
        self,
        response: Dict[str, Any],
        path: List[str],
        model_class: Type[T]
    ) -> T | None:
        """Helper to extract and validate single item from nested API responses.
        
        Args:
            response: The API response dictionary
            path: List of keys to traverse (e.g., ["ndcStatus"])
            model_class: Pydantic model class to validate the item
            
        Returns:
            Validated model instance or None if not found/invalid
        """
        current = response
        for key in path:
            current = current.get(key)
            if not current:
                return None
        
        if not isinstance(current, dict):
            return None
            
        try:
            return model_class.model_validate(current)
        except ValidationError as e:
            logger.warning(f"Failed to validate {model_class.__name__}: {e}")
            return None

    async def check_health(self) -> bool:
        """Check if RxNorm API is accessible.
        
        Returns:
            True if API is healthy and responding with expected structure
            
        Raises:
            aiohttp.ClientError: If API is not accessible
        """
        try:
            # Use a simple endpoint to test connectivity
            response = await self._make_api_request("version")
            
            # Verify response has expected structure
            return "apiVersion" in response
        except RxNormConnectionError:
            logger.error("RxNorm API health check failed - connection error")
            raise
        except RxNormHTTPError:
            logger.error("RxNorm API health check failed - HTTP error")
            raise

    async def filter_by_property(
        self,
        rxcui: str,
        prop_name: RxNormPropertyName,
        prop_values: List[str] | None = None,
    ) -> FilterByPropertyResponse:
        """Filter concept RXCUI if the predicate is true.

        Args:
            rxcui: RxNorm identifier
            prop_name: Property name to filter by
            prop_values: Values the property might have
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.filterByProperty.html
        """
        params = {
            "propName": prop_name.value,
        }
        if prop_values:
            params["propValues"] = "+".join(prop_values)

        response = await self._make_api_request(f"rxcui/{rxcui}/filter", params)
        return FilterByPropertyResponse.model_validate(response)

    async def find_related_ndcs(
        self,
        ndc: str,
        relation: Literal["concept", "product", "drug"],
        ndc_status: Literal["active", "obsolete", "alien", "ALL"] = "active",
    ) -> FindRelatedNDCsResponse:
        """Find NDCs related by product or concept.

        Args:
            ndc: NDC (CMS 11-digit, or three-segment 5-3-2, 5-4-1, or 4-4-2, or two-segment 4-4, 5-3, or 5-4; no asterisks)
            relation: Group of NDCs to retrieve
            ndc_status: Status filter for NDCs to retrieve
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRelatedNDCs.html
        """
        params = {
            "ndc": ndc,
            "relation": relation,
            "ndcstatus": ndc_status,
        }
        response = await self._make_api_request("relatedndc", params)
        return FindRelatedNDCsResponse.model_validate(response)

    async def find_rxcui_by_id(
        self,
        idtype: RxNormIdType,
        id: str,
        allsrc: Literal[0, 1] = 0,
    ) -> FindRxcuiByIdResponse:
        """Find concepts associated with a specific identifier.

        Args:
            idtype: Type of identifier
            id: Identifier
            allsrc: Scope of search (0: Active concepts, 1: Current concepts)
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiById.html
        """
        params = {
            "idtype": idtype.value,
            "id": id,
            "allsrc": allsrc,
        }
        response = await self._make_api_request("rxcui", params)
        return FindRxcuiByIdResponse.model_validate(response)

    async def find_rxcui_by_string(
        self,
        name: str,
        *,
        allsrc: Literal[0, 1] = 0,
        srclist: RxNormSourceType | None = None,
        search: Literal[0, 1, 2, 9] = 0,
    ) -> List[str] | None:
        """Find concepts with a specified name.

        Args:
            name: Name of concept to find
            allsrc: Scope of search (0: Active concepts, 1: Current concepts)
            srclist: Filter: find only concepts that include an atom from among these sources
            search: Precision (0: Exact match only, 1: Normalized match, 2: Exact or Normalized, 9: Approximate match)
        
        Returns:
            List of RXCUI strings, or None if no results found
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiByString.html
        """
        params = {
            "name": name,
            "allsrc": allsrc,
            "search": search,
        }
        if srclist:
            params["srclist"] = srclist.value

        response = await self._make_api_request("rxcui", params)
        result = FindRxcuiByStringResponse.model_validate(response)
        
        if result.idGroup and result.idGroup.rxnormId:
            return result.idGroup.rxnormId
        return None

    async def get_all_concepts_by_status(
        self,
        status: Literal["Active", "Obsolete", "Quantified", "Remapped", "NotCurrent", "ALL"] = "ALL",
    ) -> List[MinConcept]:
        """Retrieve concepts with a specific status.

        Args:
            status: Status(es) of concepts to retrieve
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllConceptsByStatus.html
        """
        params = {"status": status}
        response = await self._make_api_request("allstatus", params)
        return self._extract_list_from_response(response, ["minConceptGroup", "minConcept"], MinConcept)

    async def get_all_concepts_by_tty(
        self,
        tty: List[RxNormTermType] | Literal['ALL'],
    ) -> List[MinConcept]:
        """Retrieve concepts with specified term type.

        Args:
            tty: Term type(s), or ALL
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllConceptsByTTY.html
        """
        if isinstance(tty, list):
            tty_value = "+".join([t.value for t in tty])
        else:
            tty_value = tty

        params = {"tty": tty_value}
        response = await self._make_api_request("allconcepts", params)
        return self._extract_list_from_response(response, ["minConceptGroup", "minConcept"], MinConcept)

    async def get_all_historical_ndcs(
        self,
        rxcui: str,
        history: Literal[0, 1, 2] = 2,
    ) -> List[HistoricalNDCTime]:
        """Retrieve all NDCs ever associated with concept.

        Args:
            rxcui: RxNorm identifier of a drug product
            history: NDC association type (0: presently directly, 1: ever directly, 2: ever (in)directly)
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllHistoricalNDCs.html
        """
        params = {"history": history}
        response = await self._make_api_request(f"rxcui/{rxcui}/allhistoricalndcs", params)
        return self._extract_list_from_response(response, ["historicalNdcConcept", "historicalNdcTime"], HistoricalNDCTime)

    async def get_all_ndcs_by_status(
        self,
        status: List[Literal["ACTIVE", "OBSOLETE", "ALIEN", "UNKNOWN"]] | Literal["ALL"] = "ALL",
    ) -> List[str]:
        """Retrieve NDCs with specified status.

        Args:
            status: NDC status filter
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllNDCsByStatus.html
        """
        if isinstance(status, list):
            status_value = "+".join(status)
        else:
            status_value = status

        params = {"status": status_value}
        response = await self._make_api_request("allNDCstatus", params)

        ndc_list = response.get("ndcList")
        if not ndc_list or not ndc_list.get("ndc"):
            return []

        return ndc_list["ndc"]

    async def get_all_properties(
        self,
        rxcui: str,
        prop: RxNormPropertyCategory | List[RxNormPropertyCategory] | Literal["ALL"] = "ALL",
    ) -> List[PropConcept]:
        """Retrieve concept details.

        Args:
            rxcui: RxNorm identifier
            prop: Property categories to retrieve, or ALL
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllProperties.html
        """
        params = {}
        if prop == "ALL":
            params["prop"] = "ALL"
        elif isinstance(prop, list):
            params["prop"] = "+".join([p.value for p in prop])
        else:
            params["prop"] = prop.value

        response = await self._make_api_request(f"rxcui/{rxcui}/allProperties", params)
        return self._extract_list_from_response(response, ["propConceptGroup", "propConcept"], PropConcept)

    async def get_all_related_info(
        self,
        rxcui: str,
        expand: List[Literal["genCard", "psn"]] | None = None,
    ) -> List[RelatedGroup]:
        """Retrieve related concepts.

        Args:
            rxcui: RxNorm identifier
            expand: Additional result fields to retrieve
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getAllRelatedInfo.html
        """
        params = {}
        if expand:
            params["expand"] = "+".join(expand)

        response = await self._make_api_request(f"rxcui/{rxcui}/allrelated", params)

        all_related_group = response.get("allRelatedGroup")
        if not all_related_group or not all_related_group.get("conceptGroup"):
            return []

        related_groups = []
        for concept_group in all_related_group["conceptGroup"]:
            if not concept_group or not isinstance(concept_group, dict):
                continue
            if not concept_group.get("tty") or not concept_group.get("conceptProperties"):
                continue

            concepts = concept_group.get("conceptProperties", [])
            related_concepts = []
            for concept in concepts:
                if not concept or not isinstance(concept, dict):
                    continue
                if not concept.get("rxcui") or not concept.get("name"):
                    continue
                related_concepts.append(RelatedConcept.model_validate(concept))

            if related_concepts:
                related_groups.append(
                    RelatedGroup.model_validate(
                        {"tty": concept_group["tty"], "concepts": related_concepts}
                    )
                )

        return related_groups

    async def get_approximate_match(
        self,
        term: str,
        *,
        max_entries: int = 20,
        option: Literal[0, 1] = 0,
    ) -> List[SearchCandidate]:
        """Retrieve concepts approximately matching query.

        Args:
            term: String, of which to find approximate matches
            max_entries: Coarse control of number of results
            option: Scope of search (0: Current concepts, 1: Active concepts)
        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getApproximateMatch.html
        """
        params = {
            "term": term,
            "maxEntries": max_entries,
            "option": option,
        }
        response = await self._make_api_request("approximateTerm", params)
        return self._extract_list_from_response(response, ["approximateGroup", "candidate"], SearchCandidate)

    async def get_display_terms(
        self,
    ) -> List[str]:
        """Retrieve strings for auto-completion.

        Gets the names used by RxNav for auto completion including names of
        ingredients, precise ingredients, brands, and synonyms.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getDisplayTerms.html
        """
        params = {}
        response = await self._make_api_request("displaynames", params)

        display_terms_list = response.get("displayTermsList")
        if not display_terms_list or not display_terms_list.get("term"):
            return []

        return display_terms_list["term"]

    async def get_drugs(
        self,
        name: str,
        expand: List[Literal["psn"]] | None = None,
    ) -> List[RelatedGroup]:
        """Retrieve drugs related to name.

        Gets drugs by ingredient, brand, clinical dose form, branded dose form, etc.

        Args:
            name: Name of ingredient, brand, clinical dose form, branded dose form
            expand: Additional result fields to retrieve

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getDrugs.html
        """
        params = {"name": name}
        if expand:
            params["expand"] = "+".join(expand)

        response = await self._make_api_request("drugs", params)

        drug_group = response.get("drugGroup")
        if not drug_group or not drug_group.get("conceptGroup"):
            return []

        related_groups = []
        for concept_group in drug_group["conceptGroup"]:
            if not concept_group or not isinstance(concept_group, dict):
                continue
            if not concept_group.get("tty") or not concept_group.get("conceptProperties"):
                continue

            concepts = concept_group.get("conceptProperties", [])
            related_concepts = []
            for concept in concepts:
                if not concept or not isinstance(concept, dict):
                    continue
                if not concept.get("rxcui") or not concept.get("name"):
                    continue
                related_concepts.append(RelatedConcept.model_validate(concept))

            if related_concepts:
                related_groups.append(
                    RelatedGroup.model_validate(
                        {"tty": concept_group["tty"], "concepts": related_concepts}
                    )
                )

        return related_groups

    async def get_id_types(
        self,
    ) -> List[str]:
        """Retrieve identifier types.

        Get concept identifier types that may be used with findRxcuiById.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getIdTypes.html
        """
        params = {}
        response = await self._make_api_request("idtypes", params)

        id_type_list = response.get("idTypeList")
        if not id_type_list or not id_type_list.get("idName"):
            return []

        return id_type_list["idName"]

    async def get_multi_ingred_brand(
        self,
        ingredientids: List[str],
    ) -> List[RelatedConcept]:
        """Retrieve brands with specified ingredients.

        Get the brands that contain all the ingredients specified.

        Args:
            ingredientids: Ingredient RXCUI(s) (Space-separated list)

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getMultiIngredBrand.html
        """
        params = {"ingredientids": " ".join(ingredientids)}
        response = await self._make_api_request("brands", params)
        return self._extract_list_from_response(response, ["brandGroup", "conceptProperties"], RelatedConcept)

    async def get_ndc_properties(
        self,
        id: str,
        ndc_status: List[Literal["active", "obsolete", "alien"]] | Literal["ALL"] = "active",
    ) -> List[NDCProperty]:
        """Retrieve NDC details.

        Get detailed properties about National Drug Codes from sources like DailyMed and FDA NDC Directory.

        Args:
            id: NDC (CMS 11-digit, or 5-3 or 4-4-2), or RXCUI, or FDA SPL set ID
            ndc_status: Status filter for NDCs to retrieve

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getNDCProperties.html
        """
        if isinstance(ndc_status, list):
            status_value = "+".join(ndc_status)
        else:
            status_value = ndc_status

        params = {
            "id": id,
            "ndcstatus": status_value,
        }
        response = await self._make_api_request("ndcproperties", params)
        return self._extract_list_from_response(response, ["ndcPropertyList", "ndcProperty"], NDCProperty)

    async def get_ndc_status(
        self,
        ndc: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        history: Literal[0, 1] = 0,
        altpkg: Literal[0, 1] = 0,
    ) -> NDCStatus | None:
        """Retrieve NDC status.

        Get status information for a National Drug Code with optional date filtering.

        Args:
            ndc: National Drug Code (11-digit, or 5-3-2, 5-4-1, or 4-4-2; no asterisks)
            start: Start of date interval
            end: End of date interval
            history: Number of history entries (0: All history entries, 1: Latest entry only)
            altpkg: Alternative packaging search (0: Strict NDC lookup, 1: Find alternate packaging if NDC not found)

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getNDCStatus.html
        """
        params = {"ndc": ndc, "history": history, "altpkg": altpkg}

        if start:
            params["start"] = start.strftime("%Y%m")
        if end:
            params["end"] = end.strftime("%Y%m")

        response = await self._make_api_request("ndcstatus", params)
        return self._extract_single_from_response(response, ["ndcStatus"], NDCStatus)

    async def get_ndcs(
        self,
        rxcui: str,
    ) -> List[str]:
        """Retrieve NDCs associated with concept.

        Get active National Drug Codes (NDCs) associated with the specified RxNorm concept.

        Args:
            rxcui: RxNorm identifier of a drug product

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getNDCs.html
        """
        params = {}
        response = await self._make_api_request(f"rxcui/{rxcui}/ndcs", params)

        ndc_group = response.get("ndcGroup")
        if not ndc_group:
            return []

        ndc_list = ndc_group.get("ndcList")
        if not ndc_list or not ndc_list.get("ndc"):
            return []

        return ndc_list["ndc"]

    async def get_prop_categories(
        self,
    ) -> List[RxNormPropertyCategory]:
        """Retrieve RxNav property categories.

        Get the available property categories that can be used with other RxNorm methods.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getPropCategories.html
        """
        params = {}
        response = await self._make_api_request("propCategories", params)

        prop_category_list = response.get("propCategoryList")
        if not prop_category_list or not prop_category_list.get("propCategory"):
            return []

        categories = []
        for category_str in prop_category_list["propCategory"]:
            try:
                categories.append(RxNormPropertyCategory(category_str))
            except ValueError:
                # Skip unknown categories
                continue

        return categories

    async def get_prop_names(
        self,
    ) -> List[RxNormPropertyName]:
        """Retrieve property names.

        Get the property names that may be used with the 'filterByProperty' function.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getPropNames.html
        """
        params = {}
        response = await self._make_api_request("propnames", params)

        prop_name_list = response.get("propNameList")
        if not prop_name_list or not prop_name_list.get("propName"):
            return []

        names = []
        for name_str in prop_name_list["propName"]:
            try:
                names.append(RxNormPropertyName(name_str))
            except ValueError:
                # Skip unknown property names
                continue

        return names

    async def get_proprietary_information(
        self,
        rxcui: str,
        srclist: List[RxNormSourceType] | Literal["ALL"] = "ALL",
        rxaui: str | None = None,
    ) -> List[ProprietaryInfo]:
        """Retrieve strings from source vocabularies.

        Get proprietary information from source vocabularies for the specified RxNorm concept.

        Args:
            rxcui: RxNorm identifier
            srclist: Source vocabularies
            rxaui: RxNorm atom identifier

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getProprietaryInformation.html
        """
        params = {}
        if srclist != "ALL":
            if isinstance(srclist, list):
                params["srclist"] = "+".join([s.value for s in srclist])
            else:
                params["srclist"] = srclist.value
        if rxaui:
            params["rxaui"] = rxaui

        response = await self._make_api_request(f"rxcui/{rxcui}/proprietary", params)
        return self._extract_list_from_response(response, ["proprietaryGroup", "proprietaryInfo"], ProprietaryInfo)

    async def get_reformulation_concepts(
        self,
    ) -> List[ReformulationConcept]:
        """Retrieve reformulation concept relationships.

        Get pairs of active RxNorm concepts related by "reformulation_of" relationships.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getReformulationConcepts.html
        """
        params = {}
        response = await self._make_api_request("reformulationConcepts", params)
        return self._extract_list_from_response(response, ["reformulationConceptList", "reformulationConcept"], ReformulationConcept)

    async def get_rela_paths(
        self,
        start: RxNormTermType | None = None,
        finish: RxNormTermType | None = None,
    ) -> List[RelationPath]:
        """Retrieve relationship paths.

        Get relationship paths between different term types in RxNorm.

        Args:
            start: Starting TTY (Term Type)
            finish: Ending TTY (Term Type)

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRelaPaths.html
        """
        params = {}
        if start:
            params["start"] = start.value
        if finish:
            params["finish"] = finish.value

        response = await self._make_api_request("relapaths", params)
        return self._extract_list_from_response(response, ["relationPathList", "relationPath"], RelationPath)

    async def get_rela_types(
        self,
    ) -> List[RxNormRelationshipType]:
        """Retrieve relationship types.

        Get the relationship types used in RxNorm.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRelaTypes.html
        """
        params = {}
        response = await self._make_api_request("relatypes", params)

        relation_type_list = response.get("relationTypeList")
        if not relation_type_list or not relation_type_list.get("relationType"):
            return []

        types = []
        for type_str in relation_type_list["relationType"]:
            try:
                types.append(RxNormRelationshipType(type_str))
            except ValueError:
                # Skip unknown relationship types
                continue

        return types

    async def get_related_by_relationship(
        self,
        rxcui: str,
        rela: List[RxNormRelationshipType],
        expand: List[Literal["psn"]] | None = None,
    ) -> List[RelatedGroup]:
        """Retrieve related concepts by relationship.

        Get RxNorm concepts related to the specified concept by specific relationship types.

        Args:
            rxcui: RxNorm identifier
            rela: Relationship(s)
            expand: Additional result fields to retrieve

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRelatedByRelationship.html
        """
        params = {"rela": "+".join([r.value for r in rela])}
        if expand:
            params["expand"] = "+".join(expand)

        response = await self._make_api_request(f"rxcui/{rxcui}/related", params)

        related_group = response.get("relatedGroup")
        if not related_group or not related_group.get("conceptGroup"):
            return []

        related_groups = []
        for concept_group in related_group["conceptGroup"]:
            if not concept_group or not isinstance(concept_group, dict):
                continue
            if not concept_group.get("tty") or not concept_group.get("conceptProperties"):
                continue

            concepts = concept_group.get("conceptProperties", [])
            related_concepts = []
            for concept in concepts:
                if not concept or not isinstance(concept, dict):
                    continue
                if not concept.get("rxcui") or not concept.get("name"):
                    continue
                related_concepts.append(RelatedConcept.model_validate(concept))

            if related_concepts:
                related_groups.append(
                    RelatedGroup.model_validate(
                        {"tty": concept_group["tty"], "concepts": related_concepts}
                    )
                )

        return related_groups

    async def get_related_by_type(
        self,
        rxcui: str,
        tty: List[RxNormTermType],
        expand: List[Literal["psn"]] | None = None,
    ) -> List[RelatedGroup]:
        """Retrieve related concepts by type.

        Get RxNorm concepts related to the specified concept by specific term types.

        Args:
            rxcui: RxNorm identifier
            tty: Term type(s)
            expand: Additional result fields to retrieve

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRelatedByType.html
        """
        params = {"tty": "+".join([t.value for t in tty])}
        if expand:
            params["expand"] = "+".join(expand)

        response = await self._make_api_request(f"rxcui/{rxcui}/related", params)

        related_group = response.get("relatedGroup")
        if not related_group or not related_group.get("conceptGroup"):
            return []

        related_groups = []
        for concept_group in related_group["conceptGroup"]:
            if not concept_group or not isinstance(concept_group, dict):
                continue
            if not concept_group.get("tty") or not concept_group.get("conceptProperties"):
                continue

            concepts = concept_group.get("conceptProperties", [])
            related_concepts = []
            for concept in concepts:
                if not concept or not isinstance(concept, dict):
                    continue
                if not concept.get("rxcui") or not concept.get("name"):
                    continue
                related_concepts.append(RelatedConcept.model_validate(concept))

            if related_concepts:
                related_groups.append(
                    RelatedGroup.model_validate(
                        {"tty": concept_group["tty"], "concepts": related_concepts}
                    )
                )

        return related_groups

    async def get_rx_concept_properties(
        self,
        rxcui: str,
    ) -> RelatedConcept | None:
        """Retrieve RxNorm concept properties.

        Get the properties of the specified RxNorm concept including name, term type, language, etc.

        Args:
            rxcui: RxNorm identifier

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxConceptProperties.html
        """
        params = {}
        response = await self._make_api_request(f"rxcui/{rxcui}/properties", params)
        return self._extract_single_from_response(response, ["properties"], RelatedConcept)

    async def get_rx_norm_name(
        self,
        rxcui: str,
    ) -> str | None:
        """Retrieve RxNorm name.

        Get the name of a concept based on its RxNorm identifier.

        Args:
            rxcui: RxNorm identifier

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxNormName.html
        """
        params = {}

        response = await self._make_api_request(f"rxcui/{rxcui}", params)

        id_group = response.get("idGroup")
        if not id_group:
            return None

        return id_group.get("name")

    async def get_rx_norm_version(
        self,
    ) -> RxNormVersionInfo:
        """Retrieve RxNorm version.

        Get the RxNorm data set version and API version.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxNormVersion.html
        """
        params = {}

        response = await self._make_api_request("version", params)

        return RxNormVersionInfo.model_validate(response)

    async def get_rx_property(
        self,
        rxcui: str,
        prop_name: RxNormPropertyName | None = None,
    ) -> List[PropConcept]:
        """Retrieve RxNorm property.

        Get property values for the specified RxNorm concept.

        Args:
            rxcui: RxNorm identifier
            prop_name: Property name

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxProperty.html
        """
        params = {}
        if prop_name:
            params["propName"] = prop_name.value

        response = await self._make_api_request(f"rxcui/{rxcui}/property", params)
        return self._extract_list_from_response(response, ["propConceptGroup", "propConcept"], PropConcept)

    async def get_rxcui_history_status(
        self,
        rxcui: str,
    ) -> dict:
        """Retrieve RXCUI history status.

        Return the status, attributes, and history of the RxNorm concept.

        Args:
            rxcui: RxNorm identifier

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRxcuiHistoryStatus.html
        """
        params = {}
        return await self._make_api_request(f"rxcui/{rxcui}/historystatus", params)

    async def get_source_types(
        self,
    ) -> List[RxNormSourceType]:
        """Retrieve source types.

        Get a list of source vocabulary abbreviations (SABs) in the current RxNorm dataset.

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getSourceTypes.html
        """
        params = {}

        response = await self._make_api_request("sourcetypes", params)

        source_type_list = response.get("sourceTypeList")
        if not source_type_list or not source_type_list.get("sourceName"):
            return []

        source_types = []
        for source_str in source_type_list["sourceName"]:
            try:
                source_types.append(RxNormSourceType(source_str))
            except ValueError:
                # Skip unknown source types
                continue

        return source_types

    async def get_spelling_suggestions(
        self,
        name: str,
    ) -> List[str]:
        """Retrieve spelling suggestions.

        Get spelling suggestions for a possibly misspelled term in decreasing order of closeness.

        Args:
            name: Possibly misspelled term

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getSpellingSuggestions.html
        """
        params = {"name": name}

        response = await self._make_api_request("spellingsuggestions", params)

        suggestion_group = response.get("suggestionGroup")
        if not suggestion_group:
            return []

        suggestion_list = suggestion_group.get("suggestionList")
        if not suggestion_list or not suggestion_list.get("suggestion"):
            return []

        return suggestion_list["suggestion"]

    async def get_term_types(
        self,
    ) -> List[RxNormTermType]:
        """Retrieve term types.

        Get concept term types in the RxNorm data set (excludes synonym term types).

        See: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getTermTypes.html
        """
        params = {}

        response = await self._make_api_request("termtypes", params)

        term_type_list = response.get("termTypeList")
        if not term_type_list or not term_type_list.get("termType"):
            return []

        term_types = []
        for term_type_str in term_type_list["termType"]:
            try:
                term_types.append(RxNormTermType(term_type_str))
            except ValueError:
                # Skip unknown term types
                continue

        return term_types
