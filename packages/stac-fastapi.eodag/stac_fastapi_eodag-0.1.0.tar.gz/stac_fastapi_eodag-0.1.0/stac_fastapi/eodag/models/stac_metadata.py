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
"""property fields."""

from collections.abc import Callable
from datetime import datetime as dt
from typing import Any, ClassVar, Optional, Union, cast
from urllib.parse import quote, unquote_plus

import attr
import orjson
from fastapi import Request
from pydantic import (
    AliasChoices,
    AliasPath,
    Field,
    field_serializer,
    model_validator,
)
from pydantic._internal._model_construction import ModelMetaclass
from pydantic.fields import FieldInfo
from stac_fastapi.types.errors import NotFoundError
from stac_fastapi.types.requests import get_base_url
from stac_fastapi.types.stac import Item
from stac_pydantic.api.extensions.sort import SortDirections, SortExtension
from stac_pydantic.api.version import STAC_API_VERSION
from stac_pydantic.item import ItemProperties
from stac_pydantic.shared import Provider
from typing_extensions import Self

from eodag.api.product._product import EOProduct
from eodag.api.product.metadata_mapping import OFFLINE_STATUS, ONLINE_STATUS, STAGING_STATUS
from eodag.utils import deepcopy, guess_file_type
from stac_fastapi.eodag.config import Settings, get_settings
from stac_fastapi.eodag.constants import ITEM_PROPERTIES_EXCLUDE
from stac_fastapi.eodag.extensions.stac import (
    BaseStacExtension,
)
from stac_fastapi.eodag.models.links import ItemLinks


class CommonStacMetadata(ItemProperties):
    """Common STAC properties."""

    # TODO: replace dt by stac_pydantic.shared.UtcDatetime.
    # Requires timezone to be set in EODAG datetime properties
    # Tested with EFAS FORECAST
    datetime: Optional[dt] = Field(default=None, validation_alias="startTimeFromAscendingNode")
    start_datetime: Optional[dt] = Field(
        default=None, validation_alias="startTimeFromAscendingNode"
    )  # TODO do not set if start = end
    end_datetime: Optional[dt] = Field(
        default=None, validation_alias="completionTimeFromAscendingNode"
    )  # TODO do not set if start = end
    created: Optional[dt] = Field(default=None, validation_alias="creationDate")
    updated: Optional[dt] = Field(default=None, validation_alias="modificationDate")
    platform: Optional[str] = Field(default=None, validation_alias="platformSerialIdentifier")
    instruments: Optional[list[str]] = Field(default=None, validation_alias="instrument")
    constellation: Optional[str] = Field(default=None, validation_alias="platform")
    providers: Optional[list[Provider]] = None
    gsd: Optional[float] = Field(default=None, validation_alias="resolution", gt=0)
    collection: Optional[str] = Field(default=None, validation_alias="productType")

    _conformance_classes: ClassVar[dict[str, str]]
    get_conformance_classes: ClassVar[Callable[[Any], list[str]]]

    @field_serializer("datetime", "start_datetime", "end_datetime", "created", "updated")
    def format_datetime(self, value: dt):
        """format datetime properties"""
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @model_validator(mode="before")
    @classmethod
    def parse_instruments(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Convert instrument ``str`` to ``list``.
        """
        if instrument := values.get("instrument"):
            values["instrument"] = (
                ",".join(instrument.split()).split(",") if isinstance(instrument, str) else instrument
            )
            if None in values["instrument"]:
                values["instrument"].remove(None)
        return values

    @model_validator(mode="before")
    @classmethod
    def parse_platform(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Convert platform ``list`` to ``str``.
        TODO: This should be removed after the refactoring of cop_marine because an item should only have one platform
        """
        if platform := values.get("platform"):
            values["platform"] = ",".join(platform) if isinstance(platform, list) else platform
        return values

    @model_validator(mode="before")
    @classmethod
    def convert_processing_level(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Convert processingLevel to ``str`` if it is ``int`"""
        if processing_level := values.get("processingLevel"):
            if isinstance(processing_level, int):
                values["processingLevel"] = f"L{processing_level}"
        return values

    @model_validator(mode="before")
    @classmethod
    def remove_id_property(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Remove "id" property which is not STAC compliant if exists.
        """
        values.pop("id", None)
        return values

    @model_validator(mode="before")
    @classmethod
    def prepare_order_status_stac_property(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare the initialization of "order:status" STAC property according to "storageStatus" EODAG property.
        """
        if "storageStatus" not in values:
            return values

        if values["storageStatus"] == OFFLINE_STATUS:
            values["status"] = "orderable"
        elif values["storageStatus"] == STAGING_STATUS:
            values["status"] = "shipping"
        else:
            values["status"] = "succeeded"
        return values

    @model_validator(mode="after")
    def validate_datetime_or_start_end(self) -> Self:
        """disable validation of datetime.

        This model is used for properties conversion not validation.
        """
        return self

    @model_validator(mode="after")
    def validate_start_end(self) -> Self:
        """disable validation of datetime.

        This model is used for properties conversion not validation.
        """
        return self

    @classmethod
    def _create_to_eodag_map(cls) -> dict[str, Optional[Union[str, AliasChoices, AliasPath]]]:
        """Create mapping to convert fields from STAC to EODAG"""
        return {v.serialization_alias or k: v.validation_alias for k, v in cls.model_fields.items()}

    @classmethod
    def to_eodag(cls, field_name: str) -> str:
        """Convert a STAC parameter to its matching EODAG name.

        Note: ``ids`` STAC parameter is not recognized since we are dealing with item properties
        """
        field_dict: dict[str, Optional[Union[str, AliasChoices, AliasPath]]] = {
            stac_name: eodag_name
            for stac_name, eodag_name in cls._create_to_eodag_map().items()
            if field_name == stac_name
        }
        if field_dict:
            if field_dict[field_name] is None:
                return field_name
            if isinstance(field_dict[field_name], (AliasChoices, AliasPath)):
                raise NotImplementedError(
                    f"Error for stac name {field_name}: AliasChoices and AliasPath are not currently handled to"
                    "convert stac names to eodag names"
                )
            return field_dict[field_name]  # type: ignore
        return field_name

    @classmethod
    def to_stac(cls, field_name: str) -> str:
        """Convert an EODAG parameter to its matching STAC name.

        Note: ``ids`` STAC parameter is not recognized since we are dealing with item properties
        """
        field_dict: dict[str, Optional[Union[str, AliasChoices, AliasPath]]] = {
            stac_name: eodag_name
            for stac_name, eodag_name in cls._create_to_eodag_map().items()
            if field_name == eodag_name
        }
        if field_dict:
            return list(field_dict.keys())[0]
        return field_name


def create_stac_metadata_model(
    extensions: Optional[list[BaseStacExtension]] = None,
    base_model: type[CommonStacMetadata] = CommonStacMetadata,
) -> type[CommonStacMetadata]:
    """Create a pydantic model to validate item properties."""
    extension_models: list[ModelMetaclass] = []

    extensions = extensions or []

    # Check extensions for additional parameters to include
    for extension in extensions:
        if extension_model := extension.FIELDS:
            extension_models.append(extension_model)

    models = [base_model] + extension_models

    model = attr.make_class(
        "StacMetadata",
        attrs={},
        bases=tuple(models),
        class_body={
            "_conformance_classes": {e.__class__.__name__: e.schema_href for e in extensions},
            "get_conformance_classes": _get_conformance_classes,
        },
    )
    return model


def get_federation_backend_dict(request: Request, provider: str) -> dict[str, Any]:
    """Generate Federation backend dict

    :param request: FastAPI request
    :param provider: provider name
    :return: Federation backend dictionary
    """
    provider_config = next(
        p for p in request.app.state.dag.providers_config.values() if provider in [p.name, getattr(p, "group", None)]
    )
    return {
        "title": getattr(provider_config, "group", provider_config.name),
        "description": getattr(provider_config, "description", None),
        "url": getattr(provider_config, "url", None),
    }


def create_stac_item(
    product: EOProduct,
    model: type[CommonStacMetadata],
    extension_is_enabled: Callable[[str], bool],
    request: Request,
    extension_names: Optional[list[str]],
    request_json: Optional[Any] = None,
) -> Item:
    """Create a STAC item from an EODAG product"""
    if product.product_type is None:
        raise NotFoundError("A STAC item can not be created from an EODAG EOProduct without collection")

    settings: Settings = get_settings()

    collection = request.app.state.dag.product_types_config.source.get(product.product_type, {}).get(
        "alias", product.product_type
    )

    feature = Item(
        type="Feature",
        assets={},
        id=product.properties["id"],
        geometry=product.geometry.__geo_interface__,
        bbox=product.geometry.bounds,
        collection=collection,
        stac_version=STAC_API_VERSION,
    )

    stac_extensions: set[str] = set()

    download_base_url = settings.download_base_url
    if not download_base_url:
        download_base_url = get_base_url(request)

    quoted_id = quote(feature["id"])
    asset_proxy_url = (
        (download_base_url + f"data/{product.provider}/{collection}/{quoted_id}")
        if extension_is_enabled("DataDownload")
        else None
    )

    settings = get_settings()
    auto_order_whitelist = settings.auto_order_whitelist
    if product.provider in auto_order_whitelist:
        # a product from a whitelisted federation backend is considered as online
        product.properties["storageStatus"] = ONLINE_STATUS

    # create assets only if product is not offline
    if (
        product.properties.get("storageStatus", ONLINE_STATUS) != OFFLINE_STATUS
        or product.provider in auto_order_whitelist
    ):
        for k, v in product.assets.items():
            # TODO: download extension with origin link (make it optional ?)
            asset_model = model.model_validate(v)
            stac_extensions.update(asset_model.get_conformance_classes())
            feature["assets"][k] = asset_model.model_dump(exclude_none=True)

            if asset_proxy_url:
                origin = deepcopy(feature["assets"][k])
                quoted_key = quote(k)
                feature["assets"][k]["href"] = asset_proxy_url + "/" + quoted_key

                origin_href = origin.get("href")
                if (
                    settings.keep_origin_url
                    and origin_href
                    and not origin_href.startswith(tuple(settings.origin_url_blacklist))
                ):
                    feature["assets"][k]["alternate"] = {"origin": origin}

        # TODO: remove downloadLink asset after EODAG assets rework
        if download_link := product.properties.get("downloadLink"):
            origin_href = download_link
            if asset_proxy_url:
                download_link = asset_proxy_url + "/downloadLink"

            mime_type = guess_file_type(origin_href) or "application/octet-stream"

            feature["assets"]["downloadLink"] = {
                "title": "Download link",
                "href": download_link,
                # TODO: download link is not always a ZIP archive
                "type": mime_type,
            }

            if settings.keep_origin_url and not origin_href.startswith(tuple(settings.origin_url_blacklist)):
                feature["assets"]["downloadLink"]["alternate"] = {
                    "origin": {
                        "title": "Origin asset link",
                        "href": origin_href,
                        # TODO: download link is not always a ZIP archive
                        "type": mime_type,
                    },
                }

    feature_model = model.model_validate({**product.properties, **{"federation:backends": [product.provider]}})
    stac_extensions.update(feature_model.get_conformance_classes())

    feature["properties"] = feature_model.model_dump(exclude_none=True, exclude=ITEM_PROPERTIES_EXCLUDE)

    feature["stac_extensions"] = list(stac_extensions)

    if extension_names and product.provider not in auto_order_whitelist:
        if "CollectionOrderExtension" in extension_names and (
            not product.properties.get("orderLink", False)
            or feature["properties"].get("order:status", "") != "orderable"
        ):
            extension_names.remove("CollectionOrderExtension")
    else:
        extension_names = []

    retrieve_body = orjson.loads(unquote_plus(product.properties.get("_dc_qs", "{}")))

    if eodag_args := getattr(request.state, "eodag_args", None):
        if provider := eodag_args.get("provider", None):
            retrieve_body["federation:backends"] = [provider]

    feature["links"] = ItemLinks(
        collection_id=collection,
        item_id=quoted_id,
        retrieve_body=retrieve_body,
        request=request,
    ).get_links(extensions=extension_names, extra_links=feature.get("links"), request_json=request_json)

    return feature


def _get_conformance_classes(self) -> list[str]:
    """Extract list of conformance classes from set fields metadata"""
    conformance_classes: set[str] = set()

    for f in self.model_fields_set:
        mf = self.model_fields.get(f)
        if not mf or not isinstance(mf, FieldInfo) or not mf.metadata:
            continue
        extension = next(
            (cast(str, m["extension"]) for m in mf.metadata if isinstance(m, dict) and "extension" in m),
            None,
        )
        if c := self._conformance_classes.get(extension, None):
            conformance_classes.add(c)

    return list(conformance_classes)


def get_sortby_to_post(get_sortby: Optional[list[str]]) -> Optional[list[SortExtension]]:
    """Convert sortby filter parameter GET syntax to POST syntax"""
    if not get_sortby:
        return None
    post_sortby: list[SortExtension] = []
    for sortby_param in get_sortby:
        sortby_param = sortby_param.strip()
        direction = "desc" if sortby_param.startswith("-") else "asc"
        field = sortby_param.lstrip("+-")
        post_sortby.append(SortExtension(field=field, direction=SortDirections(direction)))
    return post_sortby
