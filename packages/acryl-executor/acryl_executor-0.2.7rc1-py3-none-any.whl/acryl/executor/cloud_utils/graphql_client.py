# Copyright 2021 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class GraphQLClient:
    def __init__(self, gms_url: str, gms_token: str):
        self.gms_url = gms_url
        self.gms_token = gms_token

    def execute_query(
        self, query: str, variables: Optional[dict[str, Any]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Execute a GraphQL query against the DataHub API.

        Args:
            query: The GraphQL query string to execute
            variables: Optional variables for the GraphQL query

        Returns:
            Raw GraphQL response data if successful, None otherwise
        """
        try:
            request_json = {"query": query, "variables": variables or {}}

            headers = {
                "Authorization": f"Bearer {self.gms_token}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                f"{self.gms_url}/api/graphql", json=request_json, headers=headers
            )
            response.raise_for_status()

            result = response.json()
            if "errors" in result:
                logger.error(f"GraphQL errors: {result['errors']}")
                return None

            return result

        except Exception as e:
            logger.exception(f"Failed to execute GraphQL query: {e}")
            return None

    @classmethod
    def from_environment(cls) -> Optional["GraphQLClient"]:
        """
        Create GraphQLClient instance from environment variables.

        Returns:
            GraphQLClient instance if environment variables are present, None otherwise
        """
        gms_url = os.environ.get("DATAHUB_GMS_URL")
        gms_token = os.environ.get("DATAHUB_GMS_TOKEN")

        if not gms_url or not gms_token:
            logger.debug(
                "DATAHUB_GMS_URL or DATAHUB_GMS_TOKEN not found in environment"
            )
            return None

        return cls(gms_url, gms_token)
