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
from typing import Any, Optional

from acryl.executor.cloud_utils.graphql_client import GraphQLClient

logger = logging.getLogger(__name__)

CLOUD_LOGGING_CONFIGS_QUERY = """query cloudLoggingConfigsResolver {
  cloudLoggingConfigsResolver {
    s3_bucket
    s3_prefix
    remote_executor_logging_enabled
  }
}"""


class CloudLoggingConfig(GraphQLClient):
    def _parse_cloud_logging_configs_response(
        self, response_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Parse GraphQL response to extract cloud logging configuration.

        Args:
            response_data: Raw GraphQL response data

        Returns:
            Dictionary containing cloud logging configuration if found, None otherwise
        """
        if "errors" in response_data:
            logger.error(f"GraphQL errors: {response_data['errors']}")
            return None

        cloud_logging_config = response_data.get("data", {}).get(
            "cloudLoggingConfigsResolver"
        )

        if cloud_logging_config:
            logger.debug("Found cloud logging configuration")
            return {
                "s3_bucket": cloud_logging_config.get("s3_bucket"),
                "s3_prefix": cloud_logging_config.get("s3_prefix"),
                "remote_executor_logging_enabled": cloud_logging_config.get(
                    "remote_executor_logging_enabled"
                ),
            }

        logger.warning("No cloud logging configuration found")
        return None

    def get_cloud_logging_config(self) -> Optional[dict[str, Any]]:
        """
        Fetch cloud logging configuration from DataHub GraphQL API.

        Returns:
            Dictionary containing cloud logging configuration if found, None otherwise
        """
        res_data = self.execute_query(CLOUD_LOGGING_CONFIGS_QUERY)
        if res_data is None:
            logger.error("Failed to fetch cloud logging configuration")
            return None

        return self._parse_cloud_logging_configs_response(res_data)

    @classmethod
    def from_environment(cls) -> Optional["CloudLoggingConfig"]:
        """
        Create CloudLoggingConfig instance from environment variables.

        Returns:
            CloudLoggingConfig instance if environment variables are present, None otherwise
        """
        client = GraphQLClient.from_environment()
        if client is None:
            return None

        return cls(client.gms_url, client.gms_token)
