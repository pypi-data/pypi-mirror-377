# -*- coding: utf-8 -*-
# Copyright 2025, CS GROUP - France, https://www.cs-soprasteria.com
#
# This file is part of stac-fastapi-eodag project
#     https://www.github.com/CS-SI/stac-fastapi-eodag
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Search tests."""

import pytest
from eodag.api.product.metadata_mapping import ONLINE_STATUS
from eodag.utils import format_dict_items

from stac_fastapi.eodag.config import get_settings
from stac_fastapi.eodag.constants import DEFAULT_ITEMS_PER_PAGE


@pytest.mark.parametrize("bbox", [("1",), ("0,43,1",), ("0,,1",), ("a,43,1,44",)])
async def test_request_params_invalid(bbox, request_not_valid, defaults):
    """
    Test the invalid request parameters for the search endpoint.
    """
    await request_not_valid(f"search?collections={defaults.product_type}&bbox={bbox}")


@pytest.mark.parametrize("input_bbox,expected_geom", [(None, None), ("bbox_csv", "bbox_wkt")])
async def test_request_params_valid(request_valid, defaults, input_bbox, expected_geom):
    """
    Test the valid request parameters for the search endpoint.
    """
    input_qs = f"&bbox={getattr(defaults, input_bbox)}" if input_bbox else ""
    expected_kwargs = {"geom": getattr(defaults, expected_geom)} if expected_geom else {}

    await request_valid(
        f"search?collections={defaults.product_type}{input_qs}",
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            raise_errors=False,
            count=False,
            **expected_kwargs,
        ),
    )


async def test_count_search(request_valid, defaults, mock_search, mock_search_result):
    """
    Test the count setting during a search.
    """
    count = get_settings().count
    qs = f"search?collections={defaults.product_type}"

    assert count is False, "Default count setting should be False"
    response = await request_valid(
        qs,
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            raise_errors=False,
            count=False,  # Ensure count is set to False
        ),
    )
    assert response["numberMatched"] is None

    # Reset search mock, set "number_matched" attribute of the search results mock for a counting search
    # and set count to True
    mock_search.reset_mock()
    search_result = mock_search_result
    search_result.number_matched = len(search_result)
    get_settings().count = True

    response = await request_valid(
        qs,
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            raise_errors=False,
            count=True,  # Ensure count is set to True
        ),
    )
    assert response["numberMatched"] == 2

    # Reset count setting to default
    get_settings().count = count


async def test_items_response(request_valid, defaults):
    """Returned items properties must be mapped as expected"""
    resp_json = await request_valid(
        f"search?collections={defaults.product_type}",
    )
    res = resp_json["features"]
    assert len(res) == 2
    first_props = res[0]["properties"]
    assert set(res[0].keys()) == {
        "type",
        "stac_version",
        "stac_extensions",
        "bbox",
        "collection",
        "links",
        "assets",
        "id",
        "geometry",
        "properties",
    }
    assert first_props["federation:backends"] == ["peps"]
    assert first_props["datetime"] == "2018-02-15T23:53:22.871000Z"
    assert first_props["start_datetime"] == "2018-02-15T23:53:22.871000Z"
    assert first_props["end_datetime"] == "2018-02-16T00:12:14.035000Z"
    assert first_props["license"] == "other"
    assert first_props["platform"] == "S1A"
    assert first_props["instruments"] == ["SAR-C", "SAR"]
    assert first_props["eo:cloud_cover"] == 0
    assert first_props["sat:absolute_orbit"] == 20624
    assert first_props["product:type"] == "OCN"
    assert first_props["order:status"] == "succeeded"
    assert first_props["storage:tier"] == "online"
    assert "asset1" in res[0]["assets"]
    assert (
        res[0]["assets"]["asset1"]["href"]
        == f"http://testserver/data/peps/{res[0]['collection']}/{res[0]['id']}/asset1"
    )
    assert res[1]["properties"]["order:status"] == "orderable"
    assert res[1]["properties"]["storage:tier"] == "offline"
    assert "assets" in res[0]
    assert "asset1" in res[0]["assets"]
    assert (
        res[0]["assets"]["asset1"]["href"]
        == f"http://testserver/data/peps/{res[0]['collection']}/{res[0]['id']}/asset1"
    )

    # check order status and storage tier properties of the "OFFLINE" item when peps is whitelisted
    auto_order_whitelist = get_settings().auto_order_whitelist
    get_settings().auto_order_whitelist = ["peps"]

    resp_json = await request_valid(
        f"search?collections={defaults.product_type}",
    )
    res = resp_json["features"]
    assert res[1]["properties"]["order:status"] == "succeeded"
    assert res[1]["properties"]["storage:tier"] == "online"

    # restore the original auto_order_whitelist setting
    get_settings().auto_order_whitelist = auto_order_whitelist


async def test_items_response_unexpected_types(request_valid, defaults, mock_search_result):
    """Item properties contain values in unexpected types for processingLevel and platform
    These values should be tranformed so that the validation passes
    """
    result_properties = mock_search_result.data[0].properties
    result_properties["processingLevel"] = 2
    result_properties["platform"] = ["P1", "P2"]
    resp_json = await request_valid(f"search?collections={defaults.product_type}", search_result=mock_search_result)
    res = resp_json["features"]
    assert len(res) == 2
    first_props = res[0]["properties"]
    assert first_props["processing:level"] == "L2"
    assert first_props["constellation"] == "P1,P2"


async def test_assets_with_different_download_base_url(request_valid, defaults):
    """Domain for download links should be as configured in settings"""
    settings = get_settings()
    settings.download_base_url = "http://otherserver/"
    resp_json = await request_valid(
        f"search?collections={defaults.product_type}",
    )
    res = resp_json["features"]
    assert len(res) == 2
    assert "assets" in res[0]
    assert "asset1" in res[0]["assets"]
    assert (
        res[0]["assets"]["asset1"]["href"]
        == f"http://otherserver/data/peps/{res[0]['collection']}/{res[0]['id']}/asset1"
    )


async def test_no_invalid_symbols_in_urls(request_valid, defaults, mock_search_result):
    """All urls (download urls, links) should be quoted so that there are no invalid symbols"""
    result_properties = mock_search_result.data[0].properties
    result_properties["id"] = "id,with,commas"
    result_assets = mock_search_result.data[0].assets
    result_assets["asset*star"] = {"title": "asset*star", "href": "https://somewhere.fr"}
    resp_json = await request_valid(f"search?collections={defaults.product_type}", search_result=mock_search_result)
    res = resp_json["features"]
    assert len(res) == 2
    assert "," not in res[0]["assets"]["downloadLink"]
    assert res[0]["links"][1]["href"] == "http://testserver/collections/S1_SAR_OCN/items/id%2Cwith%2Ccommas"
    asset = res[0]["assets"]["asset*star"]
    assert asset["href"].endswith("asset%2Astar")


async def test_not_found(request_not_found):
    """A request to eodag server with a not supported product type must return a 404 HTTP error code"""
    await request_not_found("search?collections=ZZZ&bbox=0,43,1,44")


async def test_search_results_with_errors(request_valid, mock_search_result, defaults):
    """Search through eodag server must not display provider's error if it's not empty result"""
    errors = [
        ("usgs", Exception("foo error")),
        ("aws_eos", Exception("boo error")),
    ]
    mock_search_result.errors.extend(errors)

    await request_valid(
        f"search?collections={defaults.product_type}",
        search_result=mock_search_result,
    )


@pytest.mark.parametrize(
    ("input_start", "input_end", "expected_start", "expected_end"),
    [
        ("start", "end", "start", "end"),
        ("start", "..", "start", None),
        ("..", "end", None, "end"),
        ("start", None, "start", "start"),
        (None, None, None, None),
    ],
)
async def test_date_search(request_valid, defaults, input_start, input_end, expected_start, expected_end):
    """Search through eodag server /search endpoint using dates filering should return a valid response"""
    input_date_qs = f"&datetime={getattr(defaults, input_start, input_start)}" if input_start else ""
    input_date_qs += f"/{getattr(defaults, input_end, input_end)}" if input_end else ""

    expected_kwargs = {"start": getattr(defaults, expected_start)} if expected_start else {}
    expected_kwargs |= {"end": getattr(defaults, expected_end)} if expected_end else {}

    await request_valid(
        f"search?collections={defaults.product_type}&bbox={defaults.bbox_csv}{input_date_qs}",
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            geom=defaults.bbox_wkt,
            raise_errors=False,
            count=False,
            **expected_kwargs,
        ),
    )


@pytest.mark.parametrize("use_dates", [(False,), (True,)])
async def test_date_search_from_items(request_valid, defaults, use_dates):
    """Search through eodag server collection/items endpoint using dates filering should return a valid response"""
    input_date_qs = f"&datetime={defaults.start}/{defaults.end}" if use_dates else ""
    expected_kwargs = {"start": defaults.start, "end": defaults.end} if use_dates else {}

    await request_valid(
        f"collections/{defaults.product_type}/items?bbox={defaults.bbox_csv}{input_date_qs}",
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            geom=defaults.bbox_wkt,
            raise_errors=False,
            count=False,
            **expected_kwargs,
        ),
    )


@pytest.mark.parametrize(
    "sortby,expected_sort_by",
    [
        ("-datetime", [("startTimeFromAscendingNode", "desc")]),
        ("datetime", [("startTimeFromAscendingNode", "asc")]),
        ("-start", [("startTimeFromAscendingNode", "desc")]),
        ("start", [("startTimeFromAscendingNode", "asc")]),
        ("-end", [("completionTimeFromAscendingNode", "desc")]),
        ("end", [("completionTimeFromAscendingNode", "asc")]),
    ],
)
async def test_sortby_items_parametrize(request_valid, defaults, sortby, expected_sort_by):
    """Test sortby param with various values."""
    await request_valid(
        f"collections/{defaults.product_type}/items?sortby={sortby}",
        expected_search_kwargs={
            "productType": defaults.product_type,
            "sort_by": expected_sort_by,
            "page": 1,
            "items_per_page": 10,
            "raise_errors": False,
            "count": False,
        },
        check_links=False,
    )


async def test_sortby_invalid_field_returns_400(app_client, defaults):
    """Test sortby with an invalid field returns a 400 error and expected error structure."""
    sortby = "-unknownfield"
    response = await app_client.get(f"/collections/{defaults.product_type}/items?sortby={sortby}")
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json["code"] == "400"
    assert "ticket" in resp_json
    assert resp_json["description"] == "Something went wrong"


async def test_search_item_id_from_collection(request_valid, defaults):
    """Search by id through eodag server /collection endpoint should return a valid response"""
    await request_valid(
        f"collections/{defaults.product_type}/items/foo",
        expected_search_kwargs={
            "id": "foo",
            "productType": defaults.product_type,
        },
    )


async def test_cloud_cover_post_search(request_valid, defaults):
    """POST search with cloudCover filtering through eodag server should return a valid response"""
    await request_valid(
        "search",
        method="POST",
        post_data={
            "collections": [defaults.product_type],
            "bbox": defaults.bbox_list,
            "query": {"eo:cloud_cover": {"lte": 10}},
        },
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            cloudCover=10,
            geom=defaults.bbox_wkt,
            raise_errors=False,
            count=False,
        ),
    )


async def test_intersects_post_search(request_valid, defaults):
    """POST search with intersects filtering through eodag server should return a valid response"""
    await request_valid(
        "search",
        method="POST",
        post_data={
            "collections": [defaults.product_type],
            "intersects": defaults.bbox_geojson,
        },
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            geom=defaults.bbox_wkt,
            raise_errors=False,
            count=False,
        ),
    )


@pytest.mark.parametrize(
    ("input_start", "input_end", "expected_start", "expected_end"),
    [
        ("start", "end", "start", "end"),
        ("start", "..", "start", None),
        ("..", "end", None, "end"),
        ("start", None, "start", "start"),
    ],
)
async def test_date_post_search(request_valid, defaults, input_start, input_end, expected_start, expected_end):
    """POST search with datetime filtering through eodag server should return a valid response"""
    input_date = getattr(defaults, input_start, input_start)
    input_date += f"/{getattr(defaults, input_end, input_end)}" if input_end else ""

    expected_kwargs = {"start": getattr(defaults, expected_start)} if expected_start else {}
    expected_kwargs |= {"end": getattr(defaults, expected_end)} if expected_end else {}

    await request_valid(
        "search",
        method="POST",
        post_data={
            "collections": [defaults.product_type],
            "datetime": input_date,
        },
        expected_search_kwargs=dict(
            productType=defaults.product_type,
            page=1,
            items_per_page=DEFAULT_ITEMS_PER_PAGE,
            raise_errors=False,
            count=False,
            **expected_kwargs,
        ),
    )


async def test_ids_post_search(request_valid, defaults):
    """POST search with ids filtering through eodag server should return a valid response"""
    await request_valid(
        "search",
        method="POST",
        post_data={
            "collections": [defaults.product_type],
            "ids": ["foo", "bar"],
        },
        search_call_count=2,
        expected_search_kwargs=[
            {
                "id": "foo",
                "productType": defaults.product_type,
            },
            {
                "id": "bar",
                "productType": defaults.product_type,
            },
        ],
    )


# TODO: add test_provider_prefix_post_search when feature is ready


async def test_search_response_contains_pagination_info(request_valid, defaults):
    """Responses to valid search requests must return a geojson with pagination info in properties"""
    response = await request_valid(f"search?collections={defaults.product_type}")
    assert "numberMatched" in response
    assert "numberReturned" in response


@pytest.mark.parametrize(
    ("keep_origin_url", "origin_url_blacklist", "expected_found_alt_urls"),
    [
        (None, None, [False, False, False, False]),
        (True, None, [True, True, True, True]),
        (True, "https://peps.cnes.fr", [False, False, True, False]),
    ],
    ids=[
        "no alt links by default",
        "alt links and no blacklist",
        "alt links and blacklist",
    ],
)
async def test_assets_alt_url_blacklist(
    request_valid,
    defaults,
    mock_search_result,
    keep_origin_url,
    origin_url_blacklist,
    expected_found_alt_urls,
    settings_cache_clear,
):
    """Search through eodag server must not have alternate link if in blacklist"""

    search_result = mock_search_result
    search_result[0].assets.update({"asset1": {"href": "https://peps.cnes.fr"}})
    search_result[1].assets.update({"asset1": {"href": "https://somewhere.fr"}})
    # make assets of the second product available for this test
    search_result[1].properties["storageStatus"] = ONLINE_STATUS

    with pytest.MonkeyPatch.context() as mp:
        if keep_origin_url is not None:
            mp.setenv("KEEP_ORIGIN_URL", str(keep_origin_url))
        if origin_url_blacklist is not None:
            mp.setenv("ORIGIN_URL_BLACKLIST", origin_url_blacklist)
            mp.setenv("STAC_FASTAPI_LANDING_ID", "aaaaaaaaaaaa")

        response = await request_valid(f"search?collections={defaults.product_type}")
        response_items = [f for f in response["features"]]
        assert ["alternate" in a for i in response_items for a in i["assets"].values()] == expected_found_alt_urls


@pytest.mark.parametrize(
    ("method", "url", "post_data", "expected_kwargs"),
    [
        # POST with provider specified
        (
            "POST",
            "search",
            {"collections": ["{defaults.product_type}"], "query": {"federation:backends": {"eq": "peps"}}},
            {"provider": "peps"},
        ),
        # POST with no provider specified
        ("POST", "search", {"collections": ["{defaults.product_type}"]}, {}),
        # GET with provider specified
        (
            "GET",
            'search?collections={defaults.product_type}&query={{"federation:backends":{{"eq":"peps"}} }}',
            None,
            {"provider": "peps"},
        ),
        # GET with no provider specified
        ("GET", "search?collections={defaults.product_type}", None, {}),
    ],
    ids=[
        "POST with provider specified",
        "POST with no provider specified",
        "GET with provider specified",
        "GET with no provider specified",
    ],
)
async def test_search_provider_in_downloadlink(request_valid, defaults, method, url, post_data, expected_kwargs):
    """Search through eodag server and check that provider appears in downloadLink"""
    # format defauts values
    url = url.format(defaults=defaults)
    post_data = format_dict_items(post_data, defaults=defaults) if post_data else None

    response = await request_valid(
        url=url,
        method=method,
        post_data=post_data,
        check_links=False,
        expected_search_kwargs=dict(
            page=1,
            items_per_page=10,
            raise_errors=False,
            count=False,
            productType=defaults.product_type,
            **expected_kwargs,
        ),
    )
    response_items = [f for f in response["features"]]
    assert all(
        [i["assets"]["downloadLink"]["href"] for i in response_items if i["properties"]["order:status"] != "orderable"]
    )
