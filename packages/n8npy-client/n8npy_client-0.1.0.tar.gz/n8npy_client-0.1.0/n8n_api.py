"""Client for the n8n Public REST API."""

from __future__ import annotations

import os
import typing as t
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

load_dotenv()

JsonDict = dict[str, t.Any]
JsonMapping = t.Mapping[str, t.Any]


@dataclass
class N8nClient:
    """Thin wrapper around the n8n REST API.

    Args:
        base_url: Fully-qualified base URL, defaults to ``https://n8n.example.com/api/v1``.
        api_key: API key with access to the public API. Loaded from ``N8N_API_KEY`` if not provided.
    """

    base_url: str = os.getenv("BASE_URL", "https://n8n.example.com/api/v1")
    api_key: str = os.getenv("N8N_API_KEY", "")

    # ---------- internals ----------
    def _headers(self) -> dict[str, str]:
        """Return the HTTP headers required for authenticated requests.

        Returns:
            Dictionary containing the headers, including the ``X-N8N-API-KEY``.
        """
        if not self.api_key:
            raise RuntimeError("N8N_API_KEY is missing (check your .env file)")
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-N8N-API-KEY": self.api_key,
        }

    @staticmethod
    def _clean_params(params: t.Mapping[str, t.Any] | None) -> dict[str, t.Any]:
        """Remove ``None`` values and normalise query parameter types.

        Args:
            params: Mapping of query parameters that may include ``None`` values or sequences.

        Returns:
            Dictionary ready to be passed to :func:`requests.request`.
        """
        if not params:
            return {}
        cleaned: dict[str, t.Any] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                cleaned[key] = str(value).lower()
            elif isinstance(value, (list, tuple, set)):
                cleaned[key] = ",".join(map(str, value))
            else:
                cleaned[key] = value
        return cleaned

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: t.Mapping[str, t.Any] | None = None,
        json: t.Any = None,
        timeout: int | float | None = None,
    ) -> requests.Response:
        """Execute a raw HTTP request and raise on transport-level errors.

        Args:
            method: HTTP verb to use for the request.
            path: Absolute API path relative to ``base_url``.
            params: Optional query parameters.
            json: Optional JSON payload.
            timeout: Optional timeout override in seconds.

        Returns:
            Raw :class:`requests.Response` object.
        """
        url = f"{self.base_url}{path}"
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=self._headers(),
            params=self._clean_params(params),
            json=json,
            timeout=timeout or (60 if method.upper() in {"POST", "PUT", "PATCH"} else 30),
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            snippet = response.text.strip()
            raise RuntimeError(f"{method.upper()} {url} failed: {response.status_code} - {snippet}") from exc
        return response

    @staticmethod
    def _parse_response(response: requests.Response) -> JsonDict:
        """Parse JSON content into a dictionary.

        Args:
            response: HTTP response returned from :func:`requests.request`.

        Returns:
            Parsed JSON payload. Falls back to ``{"raw": response.text}`` when decoding fails.
        """
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    def _get(self, path: str, *, params: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """Perform a GET request and decode the JSON response.

        Args:
            path: API path to request.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self._request("GET", path, params=params, timeout=30)
        return self._parse_response(response)

    def _post(
        self,
        path: str,
        *,
        json: t.Any = None,
        params: t.Mapping[str, t.Any] | None = None,
    ) -> JsonDict:
        """Perform a POST request and decode the JSON response.

        Args:
            path: API path to request.
            json: Optional JSON payload to send in the body.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self._request("POST", path, params=params, json=json, timeout=60)
        return self._parse_response(response)

    def _patch(
        self,
        path: str,
        *,
        json: t.Any = None,
        params: t.Mapping[str, t.Any] | None = None,
    ) -> JsonDict:
        """Perform a PATCH request and decode the JSON response.

        Args:
            path: API path to request.
            json: Optional JSON payload to send in the body.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self._request("PATCH", path, params=params, json=json, timeout=60)
        return self._parse_response(response)

    def _put(
        self,
        path: str,
        *,
        json: t.Any = None,
        params: t.Mapping[str, t.Any] | None = None,
    ) -> JsonDict:
        """Perform a PUT request and decode the JSON response.

        Args:
            path: API path to request.
            json: Optional JSON payload to send in the body.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self._request("PUT", path, params=params, json=json, timeout=60)
        return self._parse_response(response)

    def _delete(
        self,
        path: str,
        *,
        params: t.Mapping[str, t.Any] | None = None,
    ) -> JsonDict:
        """Perform a DELETE request and decode the JSON response.

        Args:
            path: API path to request.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        response = self._request("DELETE", path, params=params, timeout=30)
        return self._parse_response(response)

    # ---------- Raw endpoints (auto-generated from OpenAPI) ----------
    def generate_audit(self,
            *,
            additionalOptions: dict[str, t.Any] | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /audit - Generate an audit

    Generate a security audit for your n8n instance.

    Args:
        additionalOptions: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/audit'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if additionalOptions is not None: body['additionalOptions'] = additionalOptions
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def create_credential(self,
            *,
            id: str | None = None,
            name: str,
            type: str,
            data: dict[str, t.Any],
            createdAt: str | None = None,
            updatedAt: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /credentials - Create a credential

    Creates a credential that can be used by nodes of the specified type.

    Args:
        id: Example: R2DjclaysHbqn778
        name: Example: Joe's Github Credentials
        type: Example: github
        data: Example: {'token': 'ada612vad6fa5df4adf5a5dsf4389adsf76da7s'}
        createdAt: Example: 2022-04-29T11:02:29.842Z
        updatedAt: Example: 2022-04-29T11:02:29.842Z
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/credentials'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id is not None: body['id'] = id
        body['name'] = name
        body['type'] = type
        body['data'] = data
        if createdAt is not None: body['createdAt'] = createdAt
        if updatedAt is not None: body['updatedAt'] = updatedAt
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def delete_credential(self,
            id: str) -> JsonDict:
        """DELETE /credentials/{id} - Delete credential by ID

    Deletes a credential from your instance. You must be the owner of the credentials

    Args:
        id: The credential ID that needs to be deleted (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/credentials/{id}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def get_credential_type(self,
            credentialTypeName: str) -> JsonDict:
        """GET /credentials/schema/{credentialTypeName} - Show credential data schema

    Args:
        credentialTypeName: The credential type name that you want to get the schema for (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/credentials/schema/{credentialTypeName}'
        params: dict[str, t.Any] | None = None
        return self._get(path, params=params)

    def get_executions(self,
            *,
            includeData: bool | None = None,
            status: str | None = None,
            workflowId: str | None = None,
            projectId: str | None = None,
            limit: float | int | None = None,
            cursor: str | None = None) -> JsonDict:
        """GET /executions - Retrieve all executions

    Retrieve all executions from your instance.

    Args:
        includeData: Whether or not to include the execution's detailed data. (query)
        status: Status to filter the executions by. (query)
        workflowId: Workflow to filter the executions by. (query)
        projectId: (query) parameter.
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)

    Returns:
        Parsed JSON response from the API."""
        path = '/executions'
        params = {'includeData': includeData, 'status': status, 'workflowId': workflowId, 'projectId': projectId, 'limit': limit, 'cursor': cursor}
        return self._get(path, params=params)

    def get_execution(self,
            id: float | int,
            *,
            includeData: bool | None = None) -> JsonDict:
        """GET /executions/{id} - Retrieve an execution

    Retrieve an execution from your instance.

    Args:
        id: The ID of the execution. (path)
        includeData: Whether or not to include the execution's detailed data. (query)

    Returns:
        Parsed JSON response from the API."""
        path = f'/executions/{id}'
        params = {'includeData': includeData}
        return self._get(path, params=params)

    def delete_execution(self,
            id: float | int) -> JsonDict:
        """DELETE /executions/{id} - Delete an execution

    Deletes an execution from your instance.

    Args:
        id: The ID of the execution. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/executions/{id}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def retry_execution(self,
            id: float | int,
            *,
            loadWorkflow: bool | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /executions/{id}/retry - Retry an execution

    Retry an execution from your instance.

    Args:
        id: The ID of the execution. (path)
        loadWorkflow: Whether to load the currently saved workflow to execute instead of the one saved at the time of the execution. If set to true, it will retry with the latest version of the workflow.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/executions/{id}/retry'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if loadWorkflow is not None: body['loadWorkflow'] = loadWorkflow
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def create_tag(self,
            *,
            id: str | None = None,
            name: str,
            createdAt: str | None = None,
            updatedAt: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /tags - Create a tag

    Create a tag in your instance.

    Args:
        id: Example: 2tUt1wbLX592XDdX
        name: Example: Production
        createdAt: Request body field.
        updatedAt: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/tags'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id is not None: body['id'] = id
        body['name'] = name
        if createdAt is not None: body['createdAt'] = createdAt
        if updatedAt is not None: body['updatedAt'] = updatedAt
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def get_tags(self,
            *,
            limit: float | int | None = None,
            cursor: str | None = None) -> JsonDict:
        """GET /tags - Retrieve all tags

    Retrieve all tags from your instance.

    Args:
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)

    Returns:
        Parsed JSON response from the API."""
        path = '/tags'
        params = {'limit': limit, 'cursor': cursor}
        return self._get(path, params=params)

    def get_tag(self,
            id: str) -> JsonDict:
        """GET /tags/{id} - Retrieves a tag

    Retrieves a tag.

    Args:
        id: The ID of the tag. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/tags/{id}'
        params: dict[str, t.Any] | None = None
        return self._get(path, params=params)

    def delete_tag(self,
            id: str) -> JsonDict:
        """DELETE /tags/{id} - Delete a tag

    Deletes a tag.

    Args:
        id: The ID of the tag. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/tags/{id}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def update_tag(self,
            id: str,
            *,
            id_: str | None = None,
            name: str,
            createdAt: str | None = None,
            updatedAt: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PUT /tags/{id} - Update a tag

    Update a tag.

    Args:
        id: The ID of the tag. (path)
        id_: Example: 2tUt1wbLX592XDdX
        name: Example: Production
        createdAt: Request body field.
        updatedAt: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/tags/{id}'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id_ is not None: body['id'] = id_
        body['name'] = name
        if createdAt is not None: body['createdAt'] = createdAt
        if updatedAt is not None: body['updatedAt'] = updatedAt
        if extra_body: body.update(dict(extra_body))
        return self._put(path, json=body, params=params)

    def get_workflows(self,
            *,
            active: bool | None = None,
            tags: str | None = None,
            name: str | None = None,
            projectId: str | None = None,
            excludePinnedData: bool | None = None,
            limit: float | int | None = None,
            cursor: str | None = None) -> JsonDict:
        """GET /workflows - Retrieve all workflows

    Retrieve all workflows from your instance.

    Args:
        active: (query) parameter.
        tags: (query) parameter.
        name: (query) parameter.
        projectId: (query) parameter.
        excludePinnedData: Set this to avoid retrieving pinned data (query)
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)

    Returns:
        Parsed JSON response from the API."""
        path = '/workflows'
        params = {'active': active, 'tags': tags, 'name': name, 'projectId': projectId, 'excludePinnedData': excludePinnedData, 'limit': limit, 'cursor': cursor}
        return self._get(path, params=params)

    def transfer_workflow(self,
            id: str,
            *,
            destinationProjectId: str,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PUT /workflows/{id}/transfer - Transfer a workflow to another project.

    Args:
        id: The ID of the workflow. (path)
        destinationProjectId: The ID of the project to transfer the workflow to.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/workflows/{id}/transfer'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        body['destinationProjectId'] = destinationProjectId
        if extra_body: body.update(dict(extra_body))
        return self._put(path, json=body, params=params)

    def transfer_credential(self,
            id: str,
            *,
            destinationProjectId: str,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PUT /credentials/{id}/transfer - Transfer a credential to another project.

    Args:
        id: The ID of the credential. (path)
        destinationProjectId: The ID of the project to transfer the credential to.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/credentials/{id}/transfer'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        body['destinationProjectId'] = destinationProjectId
        if extra_body: body.update(dict(extra_body))
        return self._put(path, json=body, params=params)

    def get_workflow_tags(self,
            id: str) -> JsonDict:
        """GET /workflows/{id}/tags - Get workflow tags

    Get workflow tags.

    Args:
        id: The ID of the workflow. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/workflows/{id}/tags'
        params: dict[str, t.Any] | None = None
        return self._get(path, params=params)

    def update_workflow_tags(self,
            id: str,
            *,
            tags: t.Sequence[t.Mapping[str, t.Any]]) -> JsonDict:
        """PUT /workflows/{id}/tags - Update tags of a workflow

    Update tags of a workflow.

    Args:
        id: The ID of the workflow. (path)
        tags: Sequence payload sent as the JSON body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/workflows/{id}/tags'
        params: dict[str, t.Any] | None = None
        body = list(tags)
        return self._put(path, json=body, params=params)

    def get_users(self,
            *,
            limit: float | int | None = None,
            cursor: str | None = None,
            includeRole: bool | None = None,
            projectId: str | None = None) -> JsonDict:
        """GET /users - Retrieve all users

    Retrieve all users from your instance. Only available for the instance owner.

    Args:
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)
        includeRole: Whether to include the user's role or not. (query)
        projectId: (query) parameter.

    Returns:
        Parsed JSON response from the API."""
        path = '/users'
        params = {'limit': limit, 'cursor': cursor, 'includeRole': includeRole, 'projectId': projectId}
        return self._get(path, params=params)

    def create_user(self,
            *,
            users: t.Sequence[t.Mapping[str, t.Any]]) -> JsonDict:
        """POST /users - Create multiple users

    Create one or more users.

    Args:
        users: Sequence payload sent as the JSON body.

    Returns:
        Parsed JSON response from the API."""
        path = '/users'
        params: dict[str, t.Any] | None = None
        body = list(users)
        return self._post(path, json=body, params=params)

    def get_user(self,
            id: str,
            *,
            includeRole: bool | None = None) -> JsonDict:
        """GET /users/{id} - Get user by ID/Email

    Retrieve a user from your instance. Only available for the instance owner.

    Args:
        id: The ID or email of the user. (path)
        includeRole: Whether to include the user's role or not. (query)

    Returns:
        Parsed JSON response from the API."""
        path = f'/users/{id}'
        params = {'includeRole': includeRole}
        return self._get(path, params=params)

    def delete_user(self,
            id: str) -> JsonDict:
        """DELETE /users/{id} - Delete a user

    Delete a user from your instance.

    Args:
        id: The ID or email of the user. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/users/{id}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def change_role(self,
            id: str,
            *,
            newRoleName: str,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PATCH /users/{id}/role - Change a user's global role

    Args:
        id: The ID or email of the user. (path)
        newRoleName: Example: global:member
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/users/{id}/role'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        body['newRoleName'] = newRoleName
        if extra_body: body.update(dict(extra_body))
        return self._patch(path, json=body, params=params)

    def pull(self,
            *,
            force: bool | None = None,
            variables: dict[str, t.Any] | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /source-control/pull - Pull changes from the remote repository

    Requires the Source Control feature to be licensed and connected to a repository.

    Args:
        force: Example: True
        variables: Example: {'foo': 'bar'}
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/source-control/pull'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if force is not None: body['force'] = force
        if variables is not None: body['variables'] = variables
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def create_variable(self,
            *,
            id: str | None = None,
            key: str,
            value: str,
            type: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /variables - Create a variable

    Create a variable in your instance.

    Args:
        id: Request body field.
        key: Request body field.
        value: Example: test
        type: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/variables'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id is not None: body['id'] = id
        body['key'] = key
        body['value'] = value
        if type is not None: body['type'] = type
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def get_variables(self,
            *,
            limit: float | int | None = None,
            cursor: str | None = None) -> JsonDict:
        """GET /variables - Retrieve variables

    Retrieve variables from your instance.

    Args:
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)

    Returns:
        Parsed JSON response from the API."""
        path = '/variables'
        params = {'limit': limit, 'cursor': cursor}
        return self._get(path, params=params)

    def delete_variable(self,
            id: str) -> JsonDict:
        """DELETE /variables/{id} - Delete a variable

    Delete a variable from your instance.

    Args:
        id: The ID of the variable. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/variables/{id}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def update_variable(self,
            id: str,
            *,
            id_: str | None = None,
            key: str,
            value: str,
            type: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PUT /variables/{id} - Update a variable

    Update a variable from your instance.

    Args:
        id: The ID of the variable. (path)
        id_: Request body field.
        key: Request body field.
        value: Example: test
        type: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/variables/{id}'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id_ is not None: body['id'] = id_
        body['key'] = key
        body['value'] = value
        if type is not None: body['type'] = type
        if extra_body: body.update(dict(extra_body))
        return self._put(path, json=body, params=params)

    def create_project(self,
            *,
            id: str | None = None,
            name: str,
            type: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /projects - Create a project

    Create a project on your instance.

    Args:
        id: Request body field.
        name: Request body field.
        type: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = '/projects'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id is not None: body['id'] = id
        body['name'] = name
        if type is not None: body['type'] = type
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def get_projects(self,
            *,
            limit: float | int | None = None,
            cursor: str | None = None) -> JsonDict:
        """GET /projects - Retrieve projects

    Retrieve projects from your instance.

    Args:
        limit: The maximum number of items to return. (query)
        cursor: Paginate by setting the cursor parameter to the nextCursor attribute returned by the previous request's response. Default value fetches the first "page" of the collection. See pagination for more detail. (query)

    Returns:
        Parsed JSON response from the API."""
        path = '/projects'
        params = {'limit': limit, 'cursor': cursor}
        return self._get(path, params=params)

    def delete_project(self,
            projectId: str) -> JsonDict:
        """DELETE /projects/{projectId} - Delete a project

    Delete a project from your instance.

    Args:
        projectId: The ID of the project. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/projects/{projectId}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def update_project(self,
            projectId: str,
            *,
            id: str | None = None,
            name: str,
            type: str | None = None,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PUT /projects/{projectId} - Update a project

    Update a project on your instance.

    Args:
        projectId: The ID of the project. (path)
        id: Request body field.
        name: Request body field.
        type: Request body field.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/projects/{projectId}'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        if id is not None: body['id'] = id
        body['name'] = name
        if type is not None: body['type'] = type
        if extra_body: body.update(dict(extra_body))
        return self._put(path, json=body, params=params)

    def add_users_to_project(self,
            projectId: str,
            *,
            relations: t.Sequence[t.Any],
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """POST /projects/{projectId}/users - Add one or more users to a project

    Add one or more users to a project on your instance.

    Args:
        projectId: The ID of the project. (path)
        relations: A list of userIds and roles to add to the project.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/projects/{projectId}/users'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        body['relations'] = relations
        if extra_body: body.update(dict(extra_body))
        return self._post(path, json=body, params=params)

    def delete_user_from_project(self,
            projectId: str,
            userId: str) -> JsonDict:
        """DELETE /projects/{projectId}/users/{userId} - Delete a user from a project

    Delete a user from a project on your instance.

    Args:
        projectId: The ID of the project. (path)
        userId: The ID of the user. (path)

    Returns:
        Parsed JSON response from the API."""
        path = f'/projects/{projectId}/users/{userId}'
        params: dict[str, t.Any] | None = None
        return self._delete(path, params=params)

    def change_user_role_in_project(self,
            projectId: str,
            userId: str,
            *,
            role: str,
            extra_body: t.Mapping[str, t.Any] | None = None) -> JsonDict:
        """PATCH /projects/{projectId}/users/{userId} - Change a user's role in a project

    Change a user's role in a project.

    Args:
        projectId: The ID of the project. (path)
        userId: The ID of the user. (path)
        role: The role assigned to the user in the project.
        extra_body: Additional JSON properties merged into the request body.

    Returns:
        Parsed JSON response from the API."""
        path = f'/projects/{projectId}/users/{userId}'
        params: dict[str, t.Any] | None = None
        body: dict[str, t.Any] = {}
        body['role'] = role
        if extra_body: body.update(dict(extra_body))
        return self._patch(path, json=body, params=params)

    # ---------- Convenience helpers ----------
    def list_workflows(
        self,
        *,
        active: bool | None = None,
        tags: t.Sequence[str] | str | None = None,
        name: str | None = None,
        projectId: str | None = None,
        excludePinnedData: bool | None = None,
        limit: int | None = 100,
        cursor: str | None = None,
        fetch_all: bool = True,
    ) -> list[JsonDict]:
        """Iterate through ``GET /workflows`` until pagination is exhausted.

        Args:
            active: Optional filter that limits results to active workflows.
            tags: Sequence or comma separated string of tag IDs to filter by.
            name: Optional workflow name filter.
            projectId: Filter by project identifier.
            excludePinnedData: If ``True`` excludes pinned data blocks from the payload.
            limit: Page size sent to the API (max 250).
            cursor: Starting cursor returned by a previous request.
            fetch_all: When ``True`` continue following ``nextCursor`` values until empty.

        Returns:
            List of workflow dictionaries.
        """
        results: list[JsonDict] = []
        next_cursor = cursor
        while True:
            if tags is None:
                tag_param: str | None = None
            elif isinstance(tags, str):
                tag_param = tags
            else:
                tag_param = ",".join(str(tag) for tag in tags)
            page = self.get_workflows(
                active=active,
                tags=tag_param,
                name=name,
                projectId=projectId,
                excludePinnedData=excludePinnedData,
                limit=limit,
                cursor=next_cursor,
            )
            results.extend(page.get("data", []))
            next_cursor = page.get("nextCursor")
            if not (fetch_all and next_cursor):
                break
        return results

    def get_workflow(
        self,
        workflow_id: str,
        *,
        excludePinnedData: bool | None = None,
    ) -> JsonDict:
        """Fetch a single workflow by identifier.

        Args:
            workflow_id: The workflow identifier returned by the API.
            excludePinnedData: When ``True`` skips pinned data in the response.

        Returns:
            Workflow payload as provided by the API.
        """
        return self._get(
            f"/workflows/{workflow_id}",
            params={"excludePinnedData": excludePinnedData},
        )

    def create_workflow(
        self,
        *,
        name: str,
        nodes: t.Sequence[JsonMapping],
        connections: JsonMapping,
        settings: JsonMapping | None = None,
        projectId: str | None = None,
        pinData: JsonMapping | None = None,
        meta: JsonMapping | None = None,
        staticData: JsonMapping | None = None,
        tags: t.Sequence[t.Any] | None = None,
        extra_body: JsonMapping | None = None,
    ) -> JsonDict:
        """Create a workflow while handling the boilerplate structure.

        Args:
            name: Workflow name.
            nodes: Sequence of node definitions.
            connections: Connection mapping between nodes.
            settings: Optional workflow settings; defaults to empty dict.
            projectId: Project identifier to associate with the workflow.
            pinData: Optional pinned data structure.
            meta: Optional metadata block.
            staticData: Optional static data object.
            tags: Optional iterable of tag dictionaries/IDs as expected by the API.
            extra_body: Additional raw fields merged into the request body.

        Returns:
            Created workflow payload.
        """
        body: JsonDict = {
            "name": name,
            "nodes": [dict(node) for node in nodes],
            "connections": dict(connections),
            "settings": dict(settings or {}),
        }
        if projectId is not None:
            body["projectId"] = projectId
        if pinData is not None:
            body["pinData"] = dict(pinData)
        if meta is not None:
            body["meta"] = dict(meta)
        if staticData is not None:
            body["staticData"] = dict(staticData)
        if tags is not None:
            body["tags"] = list(tags)
        if extra_body:
            body.update(dict(extra_body))
        return self._post("/workflows", json=body)

    def update_workflow(
        self,
        workflow_id: str,
        *,
        extra_body: JsonMapping | None = None,
        **fields: t.Any,
    ) -> JsonDict:
        """Update a workflow by merging partial fields before issuing ``PUT``.

        Args:
            workflow_id: Workflow identifier to update.
            extra_body: Additional fields merged into the JSON body prior to sending.
            **fields: Named workflow attributes to override. Must be recognised by the API.

        Returns:
            Updated workflow payload.
        """
        if not fields and extra_body is None:
            raise ValueError("Provide at least one field to update or extra_body")

        allowed_keys = {
            "name",
            "nodes",
            "connections",
            "settings",
            "projectId",
            "pinData",
            "meta",
            "staticData",
            "tags",
            "versionId",
        }
        invalid = [key for key in fields if key not in allowed_keys]
        if invalid:
            raise ValueError(f"Unsupported workflow field(s): {', '.join(invalid)}")

        current = self.get_workflow(workflow_id)
        body: JsonDict = {key: current.get(key) for key in allowed_keys if key in current}
        body["nodes"] = current.get("nodes", []) or []
        body["connections"] = current.get("connections", {}) or {}
        body["settings"] = dict(current.get("settings") or {})

        for key, value in fields.items():
            if key == "tags" and value is not None and not isinstance(value, list):
                if isinstance(value, (tuple, set)):
                    value = list(value)
            body[key] = value

        if extra_body:
            body.update(dict(extra_body))

        return self._put(f"/workflows/{workflow_id}", json=body)

    def replace_workflow(
        self,
        workflow_id: str,
        *,
        name: str,
        nodes: t.Sequence[JsonMapping],
        connections: JsonMapping,
        settings: JsonMapping,
        **extra: t.Any,
    ) -> JsonDict:
        """Replace all workflow fields with a new definition.

        Args:
            workflow_id: Workflow identifier to replace.
            name: Workflow name.
            nodes: Complete node list that will replace the existing one.
            connections: Connection mapping describing the new workflow graph.
            settings: Workflow settings for the new definition.
            **extra: Any additional API fields appended to the payload.

        Returns:
            Updated workflow payload as returned by the API.
        """
        body: JsonDict = {
            "name": name,
            "nodes": [dict(node) for node in nodes],
            "connections": dict(connections),
            "settings": dict(settings),
        }
        for key, value in extra.items():
            body[key] = value
        return self._put(f"/workflows/{workflow_id}", json=body)

    def delete_workflow(self, workflow_id: str) -> JsonDict:
        """Delete a workflow by ID.

        Args:
            workflow_id: Workflow identifier that should be removed.

        Returns:
            API response payload (usually empty).
        """
        return self._delete(f"/workflows/{workflow_id}")

    def activate_workflow(self, workflow_id: str) -> JsonDict:
        """Activate a workflow so scheduled or trigger nodes can run.

        Args:
            workflow_id: Workflow identifier to activate.

        Returns:
            API response payload.
        """
        return self._post(f"/workflows/{workflow_id}/activate")

    def deactivate_workflow(self, workflow_id: str) -> JsonDict:
        """Deactivate a workflow to stop scheduled or trigger executions.

        Args:
            workflow_id: Workflow identifier to deactivate.

        Returns:
            API response payload.
        """
        return self._post(f"/workflows/{workflow_id}/deactivate")



if __name__ == "__main__":
    client = N8nClient()
    workflows = client.list_workflows(limit=50)
    print(f"Workflows: {len(workflows)}")
    if workflows:
        first = workflows[0]
        wf_id = first.get("id")
        if wf_id:
            details = client.get_workflow(wf_id)
            print(f"First workflow: {details.get('name')} ({wf_id})")

