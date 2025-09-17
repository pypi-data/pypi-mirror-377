"""Integration tests for RxNormClient using real API calls.

These tests validate that the client correctly interacts with the actual RxNorm API
and returns properly structured responses. They serve as both integration tests 
and validation that the API contract hasn't changed.
"""

import pytest

from pynorm import RxNormClient
from pynorm.types import (
    RxNormIdType,
    RxNormPropertyCategory,
    RxNormPropertyName,
    RxNormRelationshipType,
    RxNormTermType,
)


class TestRxNormClientIntegration:
    """Integration tests for RxNormClient using real API calls."""

    @pytest.fixture
    async def client(self):
        """Create a client instance for testing."""
        async with RxNormClient() as client:
            yield client

    @pytest.fixture(scope="class")  
    def known_rxcui(self) -> str:
        """Known RXCUI for testing - aspirin."""
        return "1191"  # Aspirin

    @pytest.fixture(scope="class")
    def known_ndc(self) -> str:
        """Known NDC for testing."""
        return "0781-1506-10"  # Example NDC

    @pytest.fixture(scope="class")
    def known_drug_name(self) -> str:
        """Known drug name for testing."""
        return "aspirin"

    # Health and Version Tests
    async def test_check_health(self, client: RxNormClient):
        """Test API health check."""
        is_healthy = await client.check_health()
        assert is_healthy is True

    async def test_get_rx_norm_version(self, client: RxNormClient):
        """Test getting RxNorm version info."""
        version_info = await client.get_rx_norm_version()
        
        assert version_info is not None
        assert version_info.version is not None
        assert version_info.apiVersion is not None
        assert len(version_info.version) > 0
        assert len(version_info.apiVersion) > 0

    # Search and Lookup Tests  
    async def test_find_rxcui_by_string(self, client: RxNormClient, known_drug_name: str):
        """Test finding RXCUI by drug name."""
        result = await client.find_rxcui_by_string(known_drug_name)
        
        assert result is not None
        assert len(result) > 0
        # Verify all returned IDs are numeric strings
        for rxcui in result:
            assert rxcui.isdigit()

    async def test_find_rxcui_by_id(self, client: RxNormClient):
        """Test finding RXCUI by identifier."""
        # Test with a known NDC
        result = await client.find_rxcui_by_id(
            idtype=RxNormIdType.NDC,
            id="0781-1506-10"
        )
        
        assert result is not None
        # Result may be empty if NDC is not found, but structure should be valid

    async def test_get_approximate_match(self, client: RxNormClient):
        """Test approximate matching."""
        # Use a slightly misspelled drug name
        candidates = await client.get_approximate_match("aspirn")  # Missing 'i'
        
        assert isinstance(candidates, list)
        if candidates:
            candidate = candidates[0]
            assert candidate.rxcui
            assert candidate.name
            assert candidate.score

    async def test_get_spelling_suggestions(self, client: RxNormClient):
        """Test spelling suggestions."""
        suggestions = await client.get_spelling_suggestions("aspirn")  # Misspelled
        
        assert isinstance(suggestions, list)
        if suggestions:
            assert "aspirin" in [s.lower() for s in suggestions]

    # Property and Detail Tests
    async def test_get_rx_concept_properties(self, client: RxNormClient, known_rxcui: str):
        """Test getting concept properties."""
        properties = await client.get_rx_concept_properties(known_rxcui)
        
        if properties:  # May be None if RXCUI not found
            assert properties.rxcui == int(known_rxcui)
            assert properties.name
            assert properties.tty

    async def test_get_rx_norm_name(self, client: RxNormClient, known_rxcui: str):
        """Test getting RxNorm name by RXCUI."""
        name = await client.get_rx_norm_name(known_rxcui)
        
        if name:  # May be None if RXCUI not found
            assert isinstance(name, str)
            assert len(name) > 0

    async def test_get_all_properties(self, client: RxNormClient, known_rxcui: str):
        """Test getting all properties for a concept."""
        properties = await client.get_all_properties(known_rxcui)
        
        assert isinstance(properties, list)
        if properties:
            prop = properties[0]
            assert prop.propCategory or prop.propName or prop.propValue

    async def test_get_rx_property(self, client: RxNormClient, known_rxcui: str):
        """Test getting specific property."""
        properties = await client.get_rx_property(
            known_rxcui,
            prop_name=RxNormPropertyName.PRESCRIBABLE
        )
        
        assert isinstance(properties, list)

    # NDC Tests
    async def test_get_ndcs(self, client: RxNormClient, known_rxcui: str):
        """Test getting NDCs for a concept."""
        ndcs = await client.get_ndcs(known_rxcui)
        
        assert isinstance(ndcs, list)
        if ndcs:
            # Verify NDC format
            ndc = ndcs[0]
            clean_ndc = ndc.replace("-", "")
            assert clean_ndc.isdigit()
            assert len(clean_ndc) in [10, 11]

    async def test_get_ndc_status(self, client: RxNormClient, known_ndc: str):
        """Test getting NDC status."""
        status = await client.get_ndc_status(known_ndc)
        
        # Status may be None if NDC not found
        if status:
            assert status.ndc11 or status.status

    async def test_get_ndc_properties(self, client: RxNormClient, known_ndc: str):
        """Test getting NDC properties."""
        properties = await client.get_ndc_properties(known_ndc)
        
        assert isinstance(properties, list)

    async def test_find_related_ndcs(self, client: RxNormClient, known_ndc: str):
        """Test finding related NDCs."""
        result = await client.find_related_ndcs(
            ndc=known_ndc,
            relation="concept"
        )
        
        assert result is not None
        assert isinstance(result.ndcInfoList.ndcInfo, list)

    # Relationship Tests
    async def test_get_all_related_info(self, client: RxNormClient, known_rxcui: str):
        """Test getting all related info."""
        related_groups = await client.get_all_related_info(known_rxcui)
        
        assert isinstance(related_groups, list)
        if related_groups:
            group = related_groups[0]
            assert group.tty
            assert isinstance(group.concepts, list)

    async def test_get_related_by_type(self, client: RxNormClient, known_rxcui: str):
        """Test getting related concepts by term type."""
        related_groups = await client.get_related_by_type(
            known_rxcui,
            tty=[RxNormTermType.IN]  # Ingredient
        )
        
        assert isinstance(related_groups, list)

    async def test_get_related_by_relationship(self, client: RxNormClient, known_rxcui: str):
        """Test getting related concepts by relationship."""
        related_groups = await client.get_related_by_relationship(
            known_rxcui,
            rela=[RxNormRelationshipType.has_ingredient]
        )
        
        assert isinstance(related_groups, list)

    # Drug Search Tests  
    async def test_get_drugs(self, client: RxNormClient, known_drug_name: str):
        """Test getting drugs by name."""
        drug_groups = await client.get_drugs(known_drug_name)
        
        assert isinstance(drug_groups, list)
        if drug_groups:
            group = drug_groups[0]
            assert group.tty
            assert isinstance(group.concepts, list)

    async def test_get_multi_ingred_brand(self, client: RxNormClient):
        """Test getting brands with multiple ingredients."""
        # Use known ingredient RXCUIs
        brands = await client.get_multi_ingred_brand(["1191", "7052"])  # aspirin + acetaminophen
        
        assert isinstance(brands, list)

    # Filter Tests
    async def test_filter_by_property(self, client: RxNormClient, known_rxcui: str):
        """Test filtering by property."""
        result = await client.filter_by_property(
            known_rxcui,
            prop_name=RxNormPropertyName.PRESCRIBABLE,
            prop_values=["Yes"]
        )
        
        assert result is not None

    # Metadata Tests
    async def test_get_id_types(self, client: RxNormClient):
        """Test getting available ID types."""
        id_types = await client.get_id_types()
        
        assert isinstance(id_types, list)
        assert len(id_types) > 0
        assert "NDC" in id_types

    async def test_get_prop_categories(self, client: RxNormClient):
        """Test getting property categories."""
        categories = await client.get_prop_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert RxNormPropertyCategory.CODES in categories

    async def test_get_prop_names(self, client: RxNormClient):
        """Test getting property names."""
        prop_names = await client.get_prop_names()
        
        assert isinstance(prop_names, list)
        assert len(prop_names) > 0

    async def test_get_term_types(self, client: RxNormClient):
        """Test getting term types."""
        term_types = await client.get_term_types()
        
        assert isinstance(term_types, list)
        assert len(term_types) > 0
        assert RxNormTermType.IN in term_types

    async def test_get_source_types(self, client: RxNormClient):
        """Test getting source types."""
        source_types = await client.get_source_types()
        
        assert isinstance(source_types, list)
        assert len(source_types) > 0

    async def test_get_rela_types(self, client: RxNormClient):
        """Test getting relationship types."""
        rela_types = await client.get_rela_types()
        
        assert isinstance(rela_types, list)
        assert len(rela_types) > 0

    async def test_get_rela_paths(self, client: RxNormClient):
        """Test getting relationship paths."""
        paths = await client.get_rela_paths()
        
        assert isinstance(paths, list)

    # Status and Concept Tests
    async def test_get_all_concepts_by_status(self, client: RxNormClient):
        """Test getting concepts by status - limited results."""
        concepts = await client.get_all_concepts_by_status("Active")
        
        assert isinstance(concepts, list)
        # Note: This may return a large number of concepts

    async def test_get_all_concepts_by_tty(self, client: RxNormClient):
        """Test getting concepts by term type - limited results.""" 
        concepts = await client.get_all_concepts_by_tty([RxNormTermType.IN])
        
        assert isinstance(concepts, list)
        # Note: This may return a large number of concepts

    async def test_get_all_ndcs_by_status(self, client: RxNormClient):
        """Test getting NDCs by status - very limited to avoid large results."""
        ndcs = await client.get_all_ndcs_by_status(["ACTIVE"])
        
        assert isinstance(ndcs, list)
        # Note: This returns a very large list, so we just check structure

    # Utility Tests  
    async def test_get_display_terms(self, client: RxNormClient):
        """Test getting display terms for auto-completion."""
        terms = await client.get_display_terms()
        
        assert isinstance(terms, list)
        assert len(terms) > 0

    async def test_get_reformulation_concepts(self, client: RxNormClient):
        """Test getting reformulation concepts."""
        concepts = await client.get_reformulation_concepts()
        
        assert isinstance(concepts, list)

    async def test_get_proprietary_information(self, client: RxNormClient, known_rxcui: str):
        """Test getting proprietary information."""
        info = await client.get_proprietary_information(known_rxcui)
        
        assert isinstance(info, list)

    async def test_get_all_historical_ndcs(self, client: RxNormClient, known_rxcui: str):
        """Test getting historical NDCs."""
        historical = await client.get_all_historical_ndcs(known_rxcui)
        
        assert isinstance(historical, list)

    async def test_get_rxcui_history_status(self, client: RxNormClient, known_rxcui: str):
        """Test getting RXCUI history status."""
        history = await client.get_rxcui_history_status(known_rxcui)
        
        assert isinstance(history, dict)
