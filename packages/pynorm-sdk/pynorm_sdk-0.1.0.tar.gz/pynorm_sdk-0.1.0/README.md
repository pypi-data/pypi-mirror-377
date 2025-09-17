# pynorm-sdk

A modern, async Python SDK for the RxNorm API that provides comprehensive access to drug information and terminology.

This SDK implements the official RxNorm API. For detailed API documentation, see:
https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html

## Features

- **Complete RxNorm API Coverage**: All 35+ endpoints implemented
- **Async/Await Support**: Built with aiohttp for high-performance async operations
- **Type Safety**: Full type hints with Pydantic v2 models
- **Error Handling**: Custom exception hierarchy for specific error types
- **Production Ready**: Comprehensive logging, session management, and error handling
- **Thoroughly Tested**: 100% test coverage with real API integration tests

## Installation

```bash
pip install pynorm-sdk
```

## Quick Start

```python
import asyncio
from pynorm import RxNormClient

async def main():
    async with RxNormClient() as client:
        # Check API health
        is_healthy = await client.check_health()
        print(f"API is healthy: {is_healthy}")
        
        # Search for a drug
        rxcuis = await client.find_rxcui_by_string("aspirin")
        if rxcuis:
            rxcui = rxcuis[0]
            print(f"Aspirin RXCUI: {rxcui}")
            
            # Get drug properties
            properties = await client.get_all_properties(rxcui)
            for prop in properties:
                print(f"{prop.propName}: {prop.propValue}")

asyncio.run(main())
```

## API Coverage

### Drug Search & Lookup
- `find_rxcui_by_string()` - Find RXCUIs by drug name
- `find_rxcui_by_id()` - Find RXCUIs by identifier (NDC, etc.)
- `get_approximate_match()` - Fuzzy drug name matching
- `get_spelling_suggestions()` - Get spelling corrections
- `get_drugs()` - Search drugs by name

### Concept Information
- `get_rx_concept_properties()` - Get concept details
- `get_rx_norm_name()` - Get concept name by RXCUI
- `get_all_properties()` - Get all concept properties
- `get_rx_property()` - Get specific properties

### NDC Operations
- `get_ndcs()` - Get NDCs for a concept
- `get_ndc_status()` - Check NDC status
- `get_ndc_properties()` - Get NDC properties
- `find_related_ndcs()` - Find related NDCs

### Relationships & Related Concepts
- `get_all_related_info()` - Get all related concepts
- `get_related_by_type()` - Get concepts by term type
- `get_related_by_relationship()` - Get concepts by relationship

### Filtering & Advanced Search
- `filter_by_property()` - Filter concepts by properties
- `get_multi_ingred_brand()` - Find multi-ingredient brands

### Metadata & Configuration
- `get_id_types()` - Available identifier types
- `get_prop_categories()` - Property categories
- `get_prop_names()` - Property names
- `get_term_types()` - Term types
- `get_source_types()` - Source vocabularies
- `get_rela_types()` - Relationship types

### Utility Functions
- `check_health()` - API health check
- `get_rx_norm_version()` - Get RxNorm version info
- `get_display_terms()` - Auto-completion terms

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from pynorm import RxNormClient
from pynorm.exceptions import RxNormHTTPError, RxNormValidationError

async with RxNormClient() as client:
    try:
        result = await client.find_rxcui_by_string("aspirin")
    except RxNormHTTPError as e:
        print(f"HTTP error: {e}")
    except RxNormValidationError as e:
        print(f"Validation error: {e}")
```

## Configuration

The client can be configured with custom settings:

```python
from pynorm import RxNormClient

# Custom configuration
async with RxNormClient(
    base_url="https://rxnav.nlm.nih.gov/REST",
    user_agent="MyApp/1.0"
) as client:
    # Your code here
    pass
```



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
