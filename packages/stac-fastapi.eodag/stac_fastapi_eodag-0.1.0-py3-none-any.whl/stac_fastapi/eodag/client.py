# -*- coding: utf-8 -*-
# Copyright 2024, CS GROUP - France, https://www.cs-soprasteria.com
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
"""Initialize landing page"""

from urllib.parse import urljoin

from stac_fastapi.types import stac
from stac_fastapi.types.core import AsyncBaseCoreClient
from stac_fastapi.types.requests import get_base_url

from stac_fastapi.eodag.config import get_settings
from stac_fastapi.eodag.models.stac_metadata import get_federation_backend_dict


class CustomCoreClient(AsyncBaseCoreClient):
    """Override the base method to generate a STAC landing page (GET /)."""

    async def landing_page(self, **kwargs) -> stac.LandingPage:
        """Generate a STAC landing page (GET /)."""
        landing_page = await super().landing_page(**kwargs)

        request = kwargs["request"]
        base_url = get_base_url(request)

        # Modify each link to add a title if absent
        stac_fastapi_title = get_settings().stac_fastapi_title
        if "links" in landing_page and isinstance(landing_page["links"], list):
            collections_url = urljoin(base_url, "collections")
            for link in landing_page["links"]:
                href = link.get("href", "")
                if href == base_url:
                    link["title"] = f"{stac_fastapi_title}"
                if href == collections_url:
                    link["title"] = "Collections"

        # add federation backends infos
        federation_backends = request.app.state.dag.available_providers()
        federation_dict = {fb: get_federation_backend_dict(request, fb) for fb in federation_backends}
        landing_page["federation"] = federation_dict

        landing_page["stac_extensions"].append(self.stac_metadata_model._conformance_classes["FederationExtension"])

        return landing_page
