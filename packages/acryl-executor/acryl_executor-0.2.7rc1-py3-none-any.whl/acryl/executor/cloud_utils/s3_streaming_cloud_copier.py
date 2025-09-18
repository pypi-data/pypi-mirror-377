import base64
import logging
import os
from typing import Any, Optional

from acryl.executor.cloud_utils.cloud_copier import CloudCopier
from acryl.executor.cloud_utils.graphql_client import GraphQLClient

logger = logging.getLogger(__name__)


class S3StreamingCloudCopier(CloudCopier):
    """
    S3 Cloud Copier that uploads files through GMS GraphQL streaming endpoints
    instead of direct S3 access. This allows uploads through a proxy to S3.
    """

    def __init__(
        self,
        graphql_client: GraphQLClient,
        base_path: str,
        chunk_size: Optional[int] = None,
    ) -> None:
        """
        Initialize S3 streaming cloud copier.

        Args:
            graphql_client: GraphQL client for GMS communication
            base_path: S3 path prefix for uploads
            chunk_size: Maximum chunk size for uploads (optional, GMS will provide default)
        """
        self.graphql_client = graphql_client
        self.base_path = base_path
        self.chunk_size = chunk_size

    def upload(self, source_local_file: str, target_cloud_file: str) -> None:
        """
        Upload a local file to S3 via GMS streaming endpoints.

        Args:
            source_local_file: Path to local file to upload
            target_cloud_file: Target S3 key (relative path)
        """
        # Construct full S3 key with base path
        object_key = self.base_path.rstrip("/") + "/" + target_cloud_file.lstrip("/")

        # Get file info
        file_size = os.path.getsize(source_local_file)
        content_type = self._get_content_type(source_local_file)

        logger.info(
            f"Starting streaming upload of {source_local_file} to S3 key {object_key} "
            f"(size: {file_size} bytes)"
        )

        try:
            # Step 1: Start streaming upload session
            upload_session = self._start_streaming_upload(
                object_key=object_key,
                content_type=content_type,
                content_length=file_size,
            )

            upload_id = upload_session["uploadId"]
            max_chunk_size = self.chunk_size or upload_session["maxChunkSize"]

            logger.debug(
                f"Started upload session {upload_id} with max chunk size {max_chunk_size}"
            )

            # Step 2: Upload file chunks
            completed_parts = self._upload_file_chunks(
                file_path=source_local_file,
                upload_id=upload_id,
                max_chunk_size=max_chunk_size,
            )

            logger.debug(f"Uploaded {len(completed_parts)} chunks")

            # Step 3: Complete upload
            completion_result = self._complete_streaming_upload(
                upload_id, completed_parts
            )

            logger.info(
                f"Successfully uploaded {source_local_file} to {completion_result['s3Location']}"
            )

        except Exception as e:
            logger.error(f"Failed to upload {source_local_file} via streaming: {e}")
            # Try to cancel partial upload if we have an upload_id
            if "upload_id" in locals():
                try:
                    self._cancel_streaming_upload(upload_id)
                    logger.debug(f"Cancelled partial upload {upload_id}")
                except Exception as cancel_error:
                    logger.warning(
                        f"Failed to cancel partial upload {upload_id}: {cancel_error}"
                    )
            raise

    def _start_streaming_upload(
        self, object_key: str, content_type: str, content_length: int
    ) -> dict[str, Any]:
        """Start S3 streaming upload session."""
        query = """
        mutation StartS3StreamingUpload($input: StartS3StreamingUploadInput!) {
            startS3StreamingUpload(input: $input) {
                uploadId
                maxChunkSize
                expiresAt
            }
        }
        """

        variables = {
            "input": {
                "objectKey": object_key,
                "contentType": content_type,
                "contentLength": content_length,
                "metadata": [
                    {"key": "uploaded-by", "value": "acryl-executor"},
                    {"key": "upload-type", "value": "ingestion-logs"},
                ],
            }
        }

        result = self.graphql_client.execute_query(query, variables)
        if not result:
            raise Exception("Failed to start streaming upload")
        return result["data"]["startS3StreamingUpload"]

    def _upload_file_chunks(
        self, file_path: str, upload_id: str, max_chunk_size: int
    ) -> list[dict[str, Any]]:
        """Upload file chunks using GraphQL mutations with base64 encoding."""
        completed_parts = []
        part_number = 1

        with open(file_path, "rb") as f:
            while True:
                # Read chunk data
                chunk_data = f.read(max_chunk_size)
                if not chunk_data:
                    break

                logger.debug(f"Uploading part {part_number} ({len(chunk_data)} bytes)")

                # Encode chunk data as base64
                base64_data = base64.b64encode(chunk_data).decode("utf-8")

                # Upload chunk via GraphQL
                chunk_result = self._upload_chunk(upload_id, part_number, base64_data)

                completed_parts.append(
                    {"partNumber": part_number, "etag": chunk_result["etag"]}
                )

                part_number += 1

        return completed_parts

    def _upload_chunk(
        self, upload_id: str, part_number: int, base64_data: str
    ) -> dict[str, Any]:
        """Upload a single chunk via GraphQL mutation."""
        query = """
        mutation UploadS3StreamingChunk($input: UploadS3StreamingChunkInput!) {
            uploadS3StreamingChunk(input: $input) {
                success
                etag
                partNumber
            }
        }
        """

        variables = {
            "input": {
                "uploadId": upload_id,
                "partNumber": part_number,
                "data": base64_data,
            }
        }

        result = self.graphql_client.execute_query(query, variables)
        if not result:
            raise Exception(f"Failed to upload chunk {part_number}")

        chunk_result = result["data"]["uploadS3StreamingChunk"]

        if not chunk_result["success"]:
            raise Exception(f"Failed to upload chunk {part_number}")

        return chunk_result

    def _complete_streaming_upload(
        self, upload_id: str, parts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Complete the S3 streaming upload."""
        query = """
        mutation CompleteS3StreamingUpload($input: CompleteS3StreamingUploadInput!) {
            completeS3StreamingUpload(input: $input) {
                s3Location
                etag
                completedAt
            }
        }
        """

        variables = {"input": {"uploadId": upload_id, "parts": parts}}

        result = self.graphql_client.execute_query(query, variables)
        if not result:
            raise Exception("Failed to complete streaming upload")
        return result["data"]["completeS3StreamingUpload"]

    def _cancel_streaming_upload(self, upload_id: str) -> dict[str, Any]:
        """Cancel an S3 streaming upload."""
        query = """
        mutation CancelS3StreamingUpload($input: CancelS3StreamingUploadInput!) {
            cancelS3StreamingUpload(input: $input) {
                success
                cancelledAt
            }
        }
        """

        variables = {"input": {"uploadId": upload_id}}

        result = self.graphql_client.execute_query(query, variables)
        if not result:
            raise Exception("Failed to cancel streaming upload")
        return result["data"]["cancelS3StreamingUpload"]

    def _get_content_type(self, file_path: str) -> str:
        """Determine content type based on file extension."""
        if file_path.endswith(".json"):
            return "application/json"
        elif file_path.endswith(".log"):
            return "text/plain"
        elif file_path.endswith(".tgz") or file_path.endswith(".tar.gz"):
            return "application/gzip"
        elif file_path.endswith(".tar"):
            return "application/x-tar"
        else:
            return "application/octet-stream"
