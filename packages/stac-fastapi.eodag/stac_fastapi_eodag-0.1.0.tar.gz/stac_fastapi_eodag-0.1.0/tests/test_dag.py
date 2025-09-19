"""Test dag module."""

from typing import Any, Dict, Iterator, List
from unittest.mock import MagicMock, patch

import pytest
from eodag import EODataAccessGateway
from eodag.utils.exceptions import RequestError, TimeOutError
from fastapi import FastAPI
from pytest_mock import MockerFixture

from stac_fastapi.eodag.dag import fetch_external_stac_collections, init_dag


@pytest.fixture(name="mock_fetch_json")
def fixture_mock_fetch_json() -> Iterator[MagicMock]:
    """
    Mock the `fetch_json` function.
    """
    with patch("stac_fastapi.eodag.dag.fetch_json") as mock:
        yield mock


@pytest.mark.parametrize(
    "product_types, fetch_json_side_effect, expected_result",
    [
        # Test case 1: Valid input
        (
            [
                {"ID": "product1", "stacCollection": "http://example.com/collection1.json"},
                {"ID": "product2", "stacCollection": "http://example.com/collection2.json"},
            ],
            [
                {"id": "collection1", "title": "Collection 1"},
                {"id": "collection2", "title": "Collection 2"},
            ],
            {
                "product1": {"id": "collection1", "title": "Collection 1"},
                "product2": {"id": "collection2", "title": "Collection 2"},
            },
        ),
        # Test case 2: Missing `stacCollection`
        (
            [
                {"ID": "product1", "stacCollection": "http://example.com/collection1.json"},
                {"ID": "product2"},  # Missing `stacCollection`
            ],
            [{"id": "collection1", "title": "Collection 1"}],
            {
                "product1": {"id": "collection1", "title": "Collection 1"},
            },
        ),
        # Test case 3: `fetch_json` raises RequestError
        (
            [
                {"ID": "product1", "stacCollection": "http://example.com/collection1.json"},
            ],
            RequestError(Exception("Mocked RequestError")),
            {
                "product1": {},
            },
        ),
        # Test case 4: `fetch_json` raises TimeOutError
        (
            [
                {"ID": "product1", "stacCollection": "http://example.com/collection1.json"},
            ],
            TimeOutError(Exception("Mocked TimeOutError")),
            {
                "product1": {},
            },
        ),
        # Test case 5: Empty input
        (
            [],
            [],
            {},
        ),
    ],
    ids=["valid input", "missing stacCollection", "requestError", "timeoutError", "empty input"],
)
def test_fetch_external_stac_collections(
    product_types: List[Dict[str, Any]],
    fetch_json_side_effect: Any,
    expected_result: Dict[str, Dict[str, Any]],
    mock_fetch_json: MagicMock,
) -> None:
    """
    Parameterized test for `fetch_external_stac_collections`.
    """
    # Arrange
    if isinstance(fetch_json_side_effect, list):
        mock_fetch_json.side_effect = fetch_json_side_effect
    else:
        mock_fetch_json.side_effect = fetch_json_side_effect

    # Act
    result = fetch_external_stac_collections(product_types)

    # Assert
    assert result == expected_result
    if product_types:
        for product_type in product_types:
            if "stacCollection" in product_type:
                mock_fetch_json.assert_any_call(product_type["stacCollection"])
    assert mock_fetch_json.call_count == len([pt for pt in product_types if "stacCollection" in pt])


@pytest.fixture(name="mock_fetch_external_stac_collections")
def fixture_mock_fetch_external_stac_collections(mocker: MockerFixture) -> MagicMock:
    """
    Mock the `fetch_external_stac_collections` function.
    """
    mock_data: dict[str, Any] = {
        "test-product": {
            "id": "test-product",
            "title": "Mocked Title",
            "description": "Mocked Description",
            "license": "Mocked License",
            "summaries": {
                "platform": ["Mocked Platform"],
                "constellation": ["Mocked Constellation"],
                "instruments": ["Mocked Instrument"],
                "processing:level": ["Mocked Level"],
            },
            "extent": {
                "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                "temporal": {"interval": [["2020-01-01T00:00:00Z", "2021-01-01T00:00:00Z"]]},
            },
            "keywords": ["keyword1", "keyword2"],
        }
    }
    return mocker.patch("stac_fastapi.eodag.dag.fetch_external_stac_collections", return_value=mock_data)


@pytest.fixture(name="mock_dag")
def fixture_mock_dag() -> MagicMock:
    """
    Mock the EODataAccessGateway object.
    """
    mock_dag = MagicMock(spec=EODataAccessGateway)
    mock_dag.list_product_types.return_value = [{"ID": "test-product", "stacCollection": "mocked_url"}]
    mock_dag.product_types_config = MagicMock()
    # Set a default value for `product_types_config.source`
    mock_dag.product_types_config.source = {}
    mock_dag._plugins_manager = MagicMock()  # pylint: disable=protected-access
    mock_dag._plugins_manager.get_search_plugins = MagicMock()  # pylint: disable=protected-access
    mock_dag.available_providers = MagicMock(return_value=["provider1", "provider2"])
    return mock_dag


@pytest.mark.parametrize(
    "product_types_config_source, expected_updated_config",
    [
        # Test case 1: Empty product_types_config.source
        (
            {
                "test-product": {
                    "title": None,
                    "abstract": None,
                    "keywords": None,
                    "instrument": None,
                    "platform": None,
                    "platformSerialIdentifier": None,
                    "processingLevel": None,
                    "license": None,
                    "missionStartDate": None,
                    "missionEndDate": None,
                }
            },
            {
                "title": "Mocked Title",
                "abstract": "Mocked Description",
                "keywords": ["keyword1", "keyword2"],
                "instrument": "Mocked Instrument",
                "platform": "Mocked Constellation",
                "platformSerialIdentifier": "Mocked Platform",
                "processingLevel": "Mocked Level",
                "license": "Mocked License",
                "missionStartDate": "2020-01-01T00:00:00Z",
                "missionEndDate": "2021-01-01T00:00:00Z",
            },
        ),
        # Test case 2: Partially filled product_types_config.source
        (
            {
                "test-product": {
                    "title": "Existing Title",
                    "abstract": None,
                    "keywords": None,
                    "instrument": "Existing Instrument",
                    "platform": None,
                    "platformSerialIdentifier": None,
                    "processingLevel": None,
                    "license": None,
                    "missionStartDate": None,
                    "missionEndDate": None,
                }
            },
            {
                "title": "Existing Title",
                "abstract": "Mocked Description",
                "keywords": ["keyword1", "keyword2"],
                "instrument": "Existing Instrument",
                "platform": "Mocked Constellation",
                "platformSerialIdentifier": "Mocked Platform",
                "processingLevel": "Mocked Level",
                "license": "Mocked License",
                "missionStartDate": "2020-01-01T00:00:00Z",
                "missionEndDate": "2021-01-01T00:00:00Z",
            },
        ),
    ],
    ids=["empty source", "partially filled source"],
)
def test_init_dag(
    product_types_config_source: Dict[str, Dict[str, Any]],
    expected_updated_config: Dict[str, Any],
    mock_fetch_external_stac_collections: MagicMock,
    mock_dag: MagicMock,
    mocker: MockerFixture,
) -> None:
    """
    Parameterized test for `init_dag` to ensure it initializes the app state correctly
    with different `product_types_config.source` values.
    """
    # Arrange: Mock the EODataAccessGateway initialization
    mocker.patch("stac_fastapi.eodag.dag.EODataAccessGateway", return_value=mock_dag)

    # Set the mocked `product_types_config.source`
    mock_dag.product_types_config.source = product_types_config_source

    # Mock the FastAPI app
    mock_app = FastAPI()

    # Act: Call `init_dag`
    init_dag(mock_app)

    # Assert: Verify that `fetch_external_stac_collections` was called
    mock_fetch_external_stac_collections.assert_called_once_with(mock_dag.list_product_types.return_value)

    # Assert: Verify that `app.state.ext_stac_collections` is set correctly
    assert mock_app.state.ext_stac_collections == mock_fetch_external_stac_collections.return_value

    # Assert: Verify that `dag.product_types_config.source` was updated
    updated_config = mock_dag.product_types_config.source["test-product"]
    assert updated_config == expected_updated_config

    # Assert: Verify that `dag._plugins_manager.get_search_plugins` was called for each provider
    mock_dag.available_providers.assert_called_once()
    for provider in mock_dag.available_providers.return_value:
        mock_dag._plugins_manager.get_search_plugins.assert_any_call(provider=provider)  # pylint: disable=protected-access
