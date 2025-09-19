import os

import requests
from heaptree.enums import Language, NodeSize, NodeType, OperatingSystem
from heaptree.exceptions import (
    HeaptreeException,
    InternalServerErrorException,
    MissingCredentialsException,
    raise_for_status,
    raise_for_auth_error,
)
from heaptree.response_wrappers import (
    CreateNodeResponseWrapper,
    ExecutionResponseWrapper,
)


class Heaptree:
    def __init__(self, api_key: str | None = None, *, base_url: str | None = None):
        """Create a new Heaptree SDK client.

        Args:
            api_key: Your platform **X-Api-Key**.
            base_url: Override the base URL of the Heaptree API (useful for local
                testing). Defaults to the hosted production endpoint.
        """

        self.api_key: str | None = api_key
        self.token: str | None = None
        self.base_url: str = base_url or "https://api.heaptree.com"

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------


    def call_api(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"

        # ----- Auth headers -----
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        else:
            raise MissingCredentialsException(
                "No api key supplied. Please set api_key"
            )

        response = requests.post(url, json=data, headers=headers)
        
        try:
            response_json = response.json()
        except ValueError as e:
            # Response is not JSON (should not happen in normal operation)
            raise HeaptreeException(
                f"Invalid JSON response for {endpoint}: {response.text}"
            ) from e
        
        # Handle HTTP error status codes
        if response.status_code == 401:
            raise_for_auth_error(response_json, "Authentication")
        elif response.status_code >= 400:
            # Generic HTTP error
            detail = response_json.get("detail", f"HTTP {response.status_code} error")
            raise HeaptreeException(f"HTTP {response.status_code}: {detail}", response_json)
            
        return response_json

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def create_node(
        self,
        os: OperatingSystem = OperatingSystem.LINUX,
        num_nodes: int = 1,
        node_type: NodeType = NodeType.UBUNTU,
        node_size: NodeSize = NodeSize.SMALL,
        lifetime_seconds: int = 330,  # 5 minutes
        applications: list[str] = [],
    ) -> CreateNodeResponseWrapper:
        """
        Create one or more nodes.

        Returns CreateNodeResponseWrapper with convenient access:
        - result.node_id (for single node)
        - result.node_ids (for multiple nodes)
        - result.web_access_url (for single node)
        - result.web_access_urls (for multiple nodes)
        
        Raises:
            UsageLimitsExceededException: When usage limits are exceeded
            InvalidRequestParametersException: When request parameters are invalid
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "os": os.value,
            "num_nodes": num_nodes,
            "node_size": node_size.value,
            "node_type": node_type.value,
            "lifetime_seconds": lifetime_seconds,
            "applications": applications,
        }
        raw_response = self.call_api("/create-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node creation")
        print(raw_response.get("details"))    
        return CreateNodeResponseWrapper(raw_response)

    def cleanup_node(self, node_id: str):
        """
        Clean up a node by terminating it and removing associated resources.
        
        Args:
            node_id: The ID of the node to clean up
            
        Returns:
            dict: Response containing cleanup status and details
            
        Raises:
            NodeNotFoundException: When the specified node is not found
            AccessDeniedException: When access to the node is denied
            InvalidNodeStateException: When the node is in an invalid state
            InternalServerErrorException: When an internal server error occurs
        """
        data = {
            "node_id": node_id,
        }
        raw_response = self.call_api("/cleanup-node", data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(raw_response, "Node cleanup")
        print(raw_response.get("details"))
        return raw_response

    def terminate_nodes(self, node_ids: list[str]):
        data = {"node_ids": node_ids}
        return self.call_api("/terminate-nodes", data)

    # ------------------------------------------------------------------
    # Remote command execution
    # ------------------------------------------------------------------

    def run_command(self, node_id: str, command: str) -> ExecutionResponseWrapper:
        """Execute a command on the remote node.
        
        Args:
            node_id: Target node.
            command: Command to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "command": command}
        raw_response = self.call_api("/run-command", data)
        return ExecutionResponseWrapper(raw_response)

    def run_code(self, node_id: str, lang: "Language", code: str) -> ExecutionResponseWrapper:
        """Execute **code** on the remote *node*.

        Args:
            node_id: Target node.
            lang: :pyclass:`~heaptree.enums.Language` specifying the language
                runtime to use.
            code: Source code to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "lang": lang.value, "code": code}
        raw_response = self.call_api("/run-code", data)
        return ExecutionResponseWrapper(raw_response)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def upload(self, node_id: str, file_path: str, destination_path: str = None):
        """
        Upload a file to a node and transfer it to the node's filesystem.

        Args:
            node_id: The ID of the node to upload to
            file_path: Local path of the file to upload
            destination_path: Optional path on the node where file should be placed
                            (defaults to /home/ubuntu/Desktop/MY_FILES/)

        Returns:
            dict: Response containing upload status and transfer details
            
        Raises:
            FileNotFoundError: When the local file is not found
            InvalidRequestParametersException: When request parameters are invalid
            InstanceNotReadyException: When the instance is not ready for file transfer
            InvalidDestinationPathException: When the destination path is invalid
            TransferFailedException: When the file transfer fails
            InternalServerErrorException: When an internal server error occurs
        """

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract filename from path
        filename = os.path.basename(file_path)

        # Step 1: Get presigned upload URL
        upload_url_data = {"node_id": node_id, "filename": filename}
        upload_response = self.call_api("/get-upload-url", upload_url_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(upload_response, "Upload URL generation")

        # Step 2: Upload file to S3 using presigned URL
        upload_url = upload_response["upload_url"]
        fields = upload_response["fields"]

        try:
            with open(file_path, "rb") as file:
                # Prepare multipart form data
                files = {"file": (filename, file, "application/octet-stream")}

                # Upload to S3
                s3_response = requests.post(upload_url, data=fields, files=files)
                s3_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to upload file: {str(e)}")

        # Step 3: Transfer file from S3 to node filesystem
        transfer_data = {"node_id": node_id}
        if destination_path:
            transfer_data["destination_path"] = destination_path

        transfer_response = self.call_api("/transfer-files", transfer_data)
        
        # Use the clean mapping system to raise appropriate exceptions
        raise_for_status(transfer_response, "File transfer")
        print(transfer_response.get("details"))

        return transfer_response

    def download(self, node_id: str, remote_path: str, local_path: str):
        data = {
            "node_id": node_id,
            "file_path": remote_path,  # API still expects 'file_path'
        }
        response_json = self.call_api("/download-files", data)
        raise_for_status(response_json, "File download")
        print("Download in progress...")
        s3_url = response_json.get("download_url")

        if not s3_url:
            return {"error": "No download URL found."}

        try:
            download_response = requests.get(s3_url)
            download_response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(download_response.content)
            print("File downloaded successfully to local path: " + local_path)
            return {"status": "SUCCESS", "details": "File downloaded successfully", "file_path": local_path}
        except requests.exceptions.RequestException as e:
            raise InternalServerErrorException(f"Failed to download file: {e}")

    def write_files(self, node_id: str, file_path: str, content: str):
        data = {"node_id": node_id, "file_path": file_path, "content": content}
        return self.call_api("/write-files", data)

    def read_files(self, node_id: str, file_path: str):
        data = {"node_id": node_id, "file_path": file_path}
        return self.call_api("/read-files", data)