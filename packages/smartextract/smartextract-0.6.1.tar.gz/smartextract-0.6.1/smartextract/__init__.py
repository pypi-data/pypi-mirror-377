"""The smartextract SDK allows easy access to the smartextract API.

See https://docs.smartextract.ai/ for the user guide and package
documentation.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from http import HTTPStatus
from io import IOBase
from mimetypes import MimeTypes
from os.path import basename
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
)
from urllib.parse import quote as url_quote
from uuid import UUID

import httpx
from pydantic import BaseModel, EmailStr, Field, JsonValue

if TYPE_CHECKING:
    from typing import Self  # For Python ≤ 3.10


__version__ = "0.6.1"

DEFAULT_BASE_URL = "https://api.smartextract.ai"
DEFAULT_TIMEOUT = 600  # seconds

Document = Union[str, bytes, IO[bytes]]
"""Types accepted as a document.

This can be either the document content itself (as a string or bytes)
or an open file in binary reading mode.
"""

Language = Literal["de", "en"]
ResourceID = Union[str, UUID]


class BillingScheme(str, Enum):
    """Enumeration of billing schemes.

    The following options are available:
    - by_invoice: User has unlimited access.
    - per_page: Each processed document consumes one credit per page.

    """

    by_invoice = "by_invoice"
    per_page = "per_page"


class AccessLevel(str, Enum):
    """Enumeration expressing the usage rights over a resource."""

    own = "own"
    edit = "edit"
    view = "view"
    list = "list"
    run = "run"
    none = "none"


class BaseInfo(BaseModel):
    """Base class for API return values."""

    @classmethod
    def from_response(cls, r: httpx.Response) -> Self:
        """Create this object based on the output of an API request."""
        return cls(**r.json())

    def _repr_pretty_(self, p, cycle) -> None:
        p.text(f"{self.__class__.__name__}(")
        if cycle:
            p.text("...)")
            return
        with p.indent(2):
            for k, v in self:
                p.break_()
                p.text(f"{k}=")
                if isinstance(v, list):
                    p.text("[")
                    with p.indent(2):
                        for v1 in v:
                            p.break_()
                            p.pretty(v1)
                            p.text(",")
                    p.break_()
                    p.text("]")
                    continue
                if isinstance(v, dict):
                    p.text("{")
                    with p.indent(2):
                        for k1, v1 in v.items():
                            p.break_()
                            p.pretty(k1)
                            p.text(": ")
                            p.pretty(v1)
                            p.text(",")
                    p.break_()
                    p.text("}")
                    continue
                if isinstance(v, Enum):
                    v = v.value
                elif isinstance(v, (timedelta, datetime, UUID)):
                    v = str(v)
                p.pretty(v)
                p.text(",")
        p.break_()
        p.text(")")


class UserInfo(BaseInfo):
    """Details about a user including email, credit balance and billing method."""

    id: UUID
    email: EmailStr
    billing_scheme: BillingScheme
    balance: Optional[int]
    previous_refill_balance: int
    previous_refill_credits: int
    previous_refill_date: datetime


class JobInfo(BaseInfo):
    """Information about a pipeline run."""

    pipeline_id: Optional[UUID]
    filename: Optional[str]
    started_at: datetime
    duration: timedelta
    error: JsonValue


class UserPermission(BaseInfo):
    """Access permissions of a user to a resource."""

    user: EmailStr
    level: AccessLevel
    created_at: datetime
    created_by: EmailStr


class IdInfo(BaseInfo):
    """Identification of a resource."""

    id: UUID
    alias: Optional[str] = None


class ResourceInfo(IdInfo):
    """Basic information about a resource."""

    type: str = Field(description="The resource type.")
    name: str = Field(description="The resource name.")
    private_access: AccessLevel = Field(
        description="Access permissions of the current user."
    )
    public_access: AccessLevel = Field(
        description="Access permissions granted to all smartextract users."
    )
    created_at: datetime = Field(
        description="Creation date of the current revision of the resource."
    )
    created_by: EmailStr = Field(
        description="User who created the current revision ofthe resource."
    )


class LuaPipelineInfo(ResourceInfo):
    """Information about a Lua pipeline."""

    code: str = Field(description="Lua code of the pipeline.")
    template: Optional[dict] = Field(
        description="An optional extraction template this pipeline"
        " declares to return, conforming to the schema described at"
        " https://smartextract.ai/schemas/template.",
    )


class TemplatePipelineInfo(ResourceInfo):
    """Information about a template pipeline."""

    template: dict = Field(
        description="The extraction template, conforming to the schema "
        " described at https://smartextract.ai/schemas/template."
    )
    ocr_id: UUID = Field(description="OCR component used by the pipeline.")
    chat_id: UUID = Field(description="LLM component used for extraction.")
    location_chat_id: Optional[UUID] = Field(
        description="LLM component used for location analysis,"
        " or None if location analysis is disabled."
    )
    use_vision: bool = Field(description="Whether to use LLM vision in this pipeline.")


class TemplateInfo(BaseInfo):
    """Information about an extraction template."""

    id: str = Field(
        description="Template identifier, in the document_type.language form.",
        examples=["invoice.en", "bank_statement.de"],
    )
    name: str = Field(description="Localized name of the template.")
    description: str = Field(description="Localized description of the template.")
    categories: list = Field(
        description="List of business domains relevant to this template."
    )


class InboxInfo(ResourceInfo):
    """Information about an inbox.

    An inbox is a repository where documents can be stored long-term.
    Every inbox has an associated pipeline (but one pipeline
    may be associated to multiple inboxes).
    """

    document_count: int = Field(description="Total number of documents in the inbox.")
    pipeline_id: UUID = Field(
        description="Pipeline used to process documents in the inbox."
    )
    ocr_id: UUID = Field(
        description="OCR component used to search documents in the inbox."
        " Ideally (but not necessarily) should match the OCR of the inbox pipeline."
    )
    postprocessor_id: Optional[UUID] = Field(
        default=None,
        description="OCR component used to search documents in the inbox."
        " Ideally (but not necessarily) should match the OCR of the inbox pipeline.",
    )


class DocumentInfo(BaseInfo):
    """Information about a document."""

    id: UUID = Field(description="The document ID number.")
    inbox_id: UUID = Field(description="The inbox containing the document.")
    name: str = Field(description="The document file name.")
    media_type: str = Field(
        description="The type of document",
        examples=["application/pdf", "image/jpeg"],
    )
    created_at: datetime = Field(
        description="Creation date of the current version of the doucment."
    )
    created_by: EmailStr = Field(
        description="User who uploaded the current version of the document."
    )


class ExtractionInfo(BaseInfo):
    """Result of a document extraction."""

    document_id: UUID = Field(description="The document ID number.")
    document_name: str = Field(description="The document file name.")
    pipeline_id: Optional[UUID] = Field(
        description="Pipeline used to compute the extraction,"
        " or None if it is a manual correction."
    )
    created_at: datetime = Field(description="Date when the extraction was computed.")
    created_by: EmailStr = Field(
        description="User responsible for triggering the extraction compuattion."
    )
    result: JsonValue = Field(
        description="Extracted information; the data schema depends on the pipeline."
    )


class JobResult(BaseInfo):
    """Result of a pipeline run."""

    result: JsonValue = Field(
        description="Result of the pipeline run;"
        " the data schema depends on the pipeline."
    )
    error: JsonValue = Field(
        default=None,
        description="Error message, or null if the run was successful.",
    )
    log: Optional[list[str]] = Field(
        default=None,
        description="List of log messages emmited by the pipeline, if any.",
    )


InfoT = TypeVar("InfoT", bound=BaseInfo)


class Page(BaseInfo, Generic[InfoT]):
    """Abstract Class used to contain a list of information."""

    count: int = Field(
        description="Total number of matches of the query,"
        " potentially more than the returned results."
    )
    results: list[InfoT] = Field(
        description="Sorted list of results matching the search filters,"
        " including limit and offset."
    )


class ClientError(Exception):
    """Error from the smartextract client error."""

    @classmethod
    def from_response(cls, r: httpx.Response) -> Self:
        """Read error from the API's response."""
        return cls(r.reason_phrase, r.text, r.request)


def drop_none(**kwargs) -> dict[str, Any]:
    """Return a dictionary excluding any None values."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _guess_filename(document: Document) -> str | None:
    name = isinstance(document, IOBase) and getattr(document, "name", None)
    if not isinstance(name, str):
        return None
    return basename(name)


def _guess_media_type(filename: str | None = None) -> str | None:
    if filename is None:
        return None
    media_type, enc = MimeTypes().guess_type(filename)
    if enc is not None:
        raise ValueError(f"Encoded file ({enc}) is not supported.")
    return media_type


class BearerAuth(httpx.Auth):
    """httpx authentication method based on a bearer token."""

    def __init__(self, access_token: str):
        self._auth_header = f"Bearer {access_token}"

    def auth_flow(self, request: httpx.Request):
        """Add authorization header."""
        request.headers["Authorization"] = self._auth_header
        yield request


class AsyncClient:
    """smartextract API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Union[None, float, httpx.Timeout] = DEFAULT_TIMEOUT,
        token_file: Optional[str | Path] = None,
        _transport: httpx.AsyncBaseTransport | None = None,
    ):
        """Initialize AsyncClient using either an API key or username and password."""
        if username or password:
            raise RuntimeError("Password login is deprecated.")
        if api_key:
            auth: httpx.Auth = BearerAuth(api_key)
        else:
            from smartextract._oauth import OAuth2Auth

            auth = OAuth2Auth(base_url, token_file)
        self._httpx = httpx.AsyncClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            transport=_transport,
        )

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        while True:
            r = await self._httpx.request(method, url, **kwargs)
            if r.status_code == HTTPStatus.CONFLICT and (
                secs := r.headers.get("retry-after")
            ):
                await asyncio.sleep(int(secs))
                continue
            if not r.is_success:
                raise ClientError.from_response(r)
            return r

    # NOTE: All code in the "start/end of code template" block must be
    # such that it makes sense when erasing all async and await
    # keywords.  If needed, refactor the code and move more complex
    # constructs elsewhere.

    # start of code template
    async def list_templates(self, language: Language = "en") -> list[TemplateInfo]:
        """List all available templates in format name.language."""
        r = await self._request("GET", "/templates", params={"lang": language})
        return [TemplateInfo(**template) for template in r.json()]

    async def get_user_info(self, user: str = "me") -> UserInfo:
        """Request stored information and credit balance of a given user."""
        r1 = await self._request("GET", f"/users/{user}")
        r2 = await self._request("GET", f"/users/{user}/credits")
        return UserInfo(**r1.json(), **r2.json())

    async def list_user_jobs(
        self,
        user: str = "me",
        *,
        limit: int | None = None,
        offset: int | None = None,
        errors_only: bool | None = None,
    ) -> Page[JobInfo]:
        """List all a user's jobs with their duration and status.

        A job started whenever a document is passed throuh a pipeline.
        """
        r = await self._request(
            "GET",
            f"/users/{user}/jobs",
            params=drop_none(limit=limit, offset=offset, errors_only=errors_only),
        )
        return Page[JobInfo].from_response(r)

    async def set_user_credits(
        self,
        user: str,
        *,
        billing_scheme: Optional[BillingScheme] = None,
        new_credits: Optional[int] = None,
        balance: Optional[int] = None,
    ) -> None:
        """Set billing information for a user.

        billing_scheme ... a user can be billed "by_invoice" or "per_page"

        If the user is billed "per_page", they will consume
        one credit of their balance per processed page.

        Then Smartextract admins can either:

        new_credits ... add new credits to existing balance
        balance ... reset balance to new value

        """
        await self._request(
            "PATCH",
            f"/users/{user}/credits",
            json=drop_none(
                billing_scheme=billing_scheme,
                new_credits=new_credits,
                balance=balance,
            ),
        )

    async def list_resources(
        self,
        type: str | None = None,  # noqa: A002
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[IdInfo]:
        """List the ids of all the users resources.

        The user can create resources of type
        ["inbox", "template_pipeline", "lua_pipeline"]

        The user can use resources of type ["aws-ocr", "openai-chat, "anthropic-chat"]
        as input to the creation methods.

        """
        r = await self._request(
            "GET",
            "/resources",
            params=drop_none(
                type=type,
                limit=limit,
                offset=offset,
            ),
        )
        return Page[IdInfo].from_response(r)

    async def list_lua_pipelines(
        self, limit: int | None = None, offset: int | None = None
    ) -> Page[IdInfo]:
        """List the ids of all the users lua_pipelines.

        Pipelines can be started with a lua script
        by using create_lua_pipeline(...)
        """
        return await self.list_resources(
            type="lua_pipeline", limit=limit, offset=offset
        )

    async def list_template_pipelines(
        self, limit: int | None = None, offset: int | None = None
    ) -> Page[IdInfo]:
        """List all created pipelines that are based on a template."""
        return await self.list_resources(
            type="template_pipeline", limit=limit, offset=offset
        )

    async def list_inboxes(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[IdInfo]:
        """List all inboxes with the attached pipeline.

        order_by must be one of "id", "name", "date".
        """
        r = await self._request(
            "GET",
            "/inboxes",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[IdInfo].from_response(r)

    async def list_documents(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[DocumentInfo]:
        """List all documents inside an inbox.

        order_by must be one of ["id", "name", "date"]
        """
        r = await self._request(
            "GET",
            f"/inboxes/{inbox_id}/documents",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[DocumentInfo].from_response(r)

    async def get_resource_info(self, resource_id: ResourceID) -> ResourceInfo:
        """Get various information about a given resource.

        Information includes the resource type, name, access level,
        and additional details specific to the resource type.
        """
        r = await self._request("GET", f"/resources/{resource_id}")
        info = r.json()
        if info["type"] == "lua_pipeline":
            r = await self._request("GET", f"/pipelines/{resource_id}")
            return LuaPipelineInfo.from_response(r)
        if info["type"] == "template_pipeline":
            r = await self._request("GET", f"/pipelines/{resource_id}")
            return TemplatePipelineInfo.from_response(r)
        if info["type"] == "inbox":
            r = await self._request("GET", f"/inboxes/{resource_id}")
            return InboxInfo.from_response(r)
        return ResourceInfo(**info)

    async def list_permissions(
        self,
        resource_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[UserPermission]:
        """For a given resource, list all users with access rights."""
        r = await self._request(
            "GET",
            f"/resources/{resource_id}/permissions",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[UserPermission].from_response(r)

    async def create_permission(
        self, resource_id: ResourceID, user: str, level: AccessLevel
    ) -> None:
        """Allow user access to a resource."""
        await self._request(
            "POST",
            f"/resources/{resource_id}/permissions",
            json={"user": user, "level": level},
        )

    async def create_lua_pipeline(
        self,
        name: str,
        code: str,
        *,
        permissions: Optional[dict[str, AccessLevel]] = None,
    ) -> UUID:
        """Create a new pipeline by providing a lua script.

        To run the pipeline for a PDF-document use run_pipeline(..)

        In the lua script's scope the PDF is available by the variable
        "document", which is an Iterator of Pages.
        """
        r = await self._request(
            "POST",
            "/pipelines",
            json=drop_none(name=name, code=code, permissions=permissions),
        )
        return UUID(r.json()["id"])

    async def create_template_pipeline(
        self,
        name: str,
        template: Union[str, dict],
        *,
        chat_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
        permissions: Optional[dict[str, AccessLevel]] = None,
        use_vision: Optional[bool] = None,
    ) -> UUID:
        """Create a new pipeline based on a yaml-template.

        template ... consult the docs: https://docs.smartextract.ai/guide/pipelines/#templates

        chat_id ... must be of resource type "openai-chat" or "anthropic-chat"
        ocr_id ... must be of resource type "aws-ocr"

        """
        r = await self._request(
            "POST",
            "/pipelines",
            json=drop_none(
                name=name,
                template=template,
                chat_id=chat_id,
                ocr_id=ocr_id,
                permissions=permissions,
                use_vision=use_vision,
            ),
        )
        return UUID(r.json()["id"])

    async def modify_pipeline(
        self,
        pipeline_id: ResourceID,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        template: Union[None, str, dict] = None,
        chat_id: Optional[ResourceID] = None,
        location_chat_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
        use_vision: Optional[bool] = None,
    ) -> None:
        """Change details of an existing pipeline.

        Provide a new Lua script (code) for a Lua pipeline, or provide
        a new template, chat_id, ocr_id or use_vision attribute for a
        template pipeline.
        """
        await self._request(
            "PATCH",
            f"/pipelines/{pipeline_id}",
            json=drop_none(
                name=name,
                code=code,
                template=template,
                chat_id=chat_id,
                location_chat_id=location_chat_id,
                ocr_id=ocr_id,
                use_vision=use_vision,
            ),
        )

    async def run_pipeline(
        self,
        pipeline_id: ResourceID,
        document: Document,
        *,
        media_type: str | None = None,
    ) -> JobResult:
        """Process a document through an existing pipeline.

        With this method, it is not necessary to upload the document
        to an inbox.  The document and the resulting extraction are
        not persisted in the smartextract servers.

        This method waits for the processing to complete and directly
        returns the extracted data.

        Arguments:
          pipeline_id: The processing pipeline to use.
          document: The document to be processed, as a string, bytes,
            or a file in binary reading mode.
          media_type: The document media type, only required when it
            is not possible to guess.
        """
        filename = _guess_filename(document) or "document"
        media_type = media_type or _guess_media_type(filename)
        r = await self._request(
            "POST",
            f"/pipelines/{pipeline_id}/run",
            files={"document": (filename, document, media_type)},
        )
        return JobResult.from_response(r)

    async def run_anonymous_pipeline(
        self,
        document: Document,
        *,
        code: str | None = None,
        template: dict | None = None,
        media_type: str | None = None,
    ) -> JobResult:
        """Process a document without permanently creating a pipeline.

        This is useful for debugging.  Either Lua code or an
        extraction template (but not both) need to be provided.

        As with `run_pipeline`, the document and the resulting
        extraction are not persisted in the smartextract servers.

        Arguments:
          document: The document to be processed, as a string, bytes,
            or a file in binary reading mode.
          code: A Lua script, as a string.
          template: An extraction template as a dictionary following
            the schema at https://smartextract.ai/schemas/template.
          media_type: The document media type, only required when it
            is not possible to guess.
        """
        if code is None:
            if template is None:
                raise ValueError("Either code or template must be provided")
            code = json.dumps(template)
            code_type = "application/json"
        elif template is None:
            code_type = "text/lua"
        else:
            raise ValueError("Only one of code or template must be provided")

        filename = _guess_filename(document) or "document"
        media_type = media_type or _guess_media_type(filename)
        r = await self._request(
            "POST",
            "/pipelines/run",
            files={
                "document": (filename, document, media_type),
                "code": ("code", code, code_type),
            },
        )
        return JobResult.from_response(r)

    async def list_pipeline_jobs(
        self,
        pipeline_id: Optional[ResourceID],
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[JobInfo]:
        """List all pipeline runs of a pipeline."""
        r = await self._request(
            "GET",
            f"/pipelines/{pipeline_id}/jobs",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[JobInfo].from_response(r)

    async def create_inbox(
        self, name: str, pipeline_id: str, *, ocr_id: Optional[str] = None
    ) -> UUID:
        """Create container for storing documents of common type.

        Inbox must be set up with document-type specific extraction pipeline.
        """
        r = await self._request(
            "POST",
            "/inboxes",
            json=drop_none(name=name, pipeline_id=pipeline_id, ocr_id=ocr_id),
        )
        return UUID(r.json()["id"])

    async def modify_inbox(
        self,
        inbox_id: ResourceID,
        *,
        name: Optional[str] = None,
        pipeline_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
    ) -> None:
        """Set new pipeline for an inbox."""
        await self._request(
            "PATCH",
            f"/inboxes/{inbox_id}",
            json=drop_none(
                name=name,
                pipeline_id=pipeline_id,
                ocr_id=ocr_id,
            ),
        )

    async def list_inbox_jobs(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[JobInfo]:
        """List all a inbox' pipeline runs."""
        r = await self._request(
            "GET",
            f"/inboxes/{inbox_id}/jobs",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[JobInfo].from_response(r)

    async def create_document(
        self,
        inbox_id: ResourceID,
        document: Document,
        *,
        filename: str | None = None,
        media_type: str | None = None,
    ) -> UUID:
        """Add a new document to an existing inbox.

        Return the ID of the newly created document.

        Arguments:
          inbox_id: The inbox in which to add a document.
          document: The contents of new document, as a string, bytes,
            or a file in binary reading mode.
          filename: The new document's name.  This can be omitted if
            `document` is a file, in which case the file's name is
            used.
          media_type: The new document's type.  This can be omitted if
            the type can be deduced from the file name.
        """
        filename = filename or _guess_filename(document)
        if not filename:
            raise ValueError("File name needs to be specified.")

        if not media_type:
            media_type, enc = MimeTypes().guess_type(filename)
            if enc is not None:
                raise ValueError(f"Encoded file ({enc}) is not supported.")

        r = await self._request(
            "POST",
            f"/inboxes/{inbox_id}",
            files={"document": (filename, document, media_type)},
        )
        return UUID(r.json()["id"])

    async def list_extractions(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[ExtractionInfo]:
        """List all extraction results of an inbox.

        order_by must be one of ["id", "name", "date"]
        """
        r = await self._request(
            "GET",
            f"inboxes/{inbox_id}/extractions",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[ExtractionInfo].from_response(r)

    async def get_document_info(self, document_id: ResourceID) -> DocumentInfo:
        """Get name, access level and inbox location for a given document id."""
        r = await self._request("GET", f"/documents/{document_id}")
        return DocumentInfo.from_response(r)

    async def delete_document(self, document_id: ResourceID) -> None:
        """Delete document from database."""
        await self._request("DELETE", f"/documents/{document_id}")

    async def get_document_bytes(self, document_id: ResourceID) -> bytes:
        """Get document content in bytes."""
        r = await self._request("GET", f"/documents/{document_id}/blob")
        return r.content

    async def get_document_extraction(
        self, document_id: ResourceID, *, recompute: bool = False
    ) -> ExtractionInfo:
        """Get the document extraction from its latest pipeline processing."""
        if recompute:
            r = await self._request(
                "POST",
                f"/documents/{document_id}/extraction",
                params={"recompute": True},
            )
            if not r.is_success:
                raise ClientError.from_response(r)
        r = await self._request(
            "GET",
            f"/documents/{document_id}/extraction",
        )
        return ExtractionInfo.from_response(r)

    async def set_document_extraction(
        self, document_id: ResourceID, extraction: JsonValue
    ) -> None:
        """Manually override the extraction data of the given document."""
        await self._request(
            "POST", f"/documents/{document_id}/extraction", json=extraction
        )

    async def create_dataset_item(
        self, dataset_id: ResourceID, key: str, value: JsonValue
    ):
        """Add item to a dataset."""
        key = url_quote(key)
        await self._request("POST", f"/datasets/{dataset_id}/items/{key}", json=value)

    async def delete_dataset_item(self, dataset_id: ResourceID, key: str):
        """Add item to a dataset."""
        key = url_quote(key)
        await self._request("DELETE", f"/datasets/{dataset_id}/items/{key}")

    # end of code template


class Client:
    """smartextract API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Union[None, float, httpx.Timeout] = DEFAULT_TIMEOUT,
        token_file: Optional[str | Path] = None,
    ):
        """Initialize the Client using either an API key or username and password."""
        if username or password:
            raise RuntimeError("Password login is deprecated.")
        if api_key:
            auth: httpx.Auth = BearerAuth(api_key)
        else:
            from smartextract._oauth import OAuth2Auth

            auth = OAuth2Auth(base_url, token_file)
        self._httpx = httpx.Client(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
        )

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        while True:
            r = self._httpx.request(method, url, **kwargs)
            if r.status_code == HTTPStatus.CONFLICT and (
                secs := r.headers.get("retry-after")
            ):
                time.sleep(int(secs))
                continue
            if not r.is_success:
                raise ClientError.from_response(r)
            return r

    def _sleep_for_retry(self, r: httpx.Response) -> None:
        s = int(r.headers.get("retry-after", 1))
        time.sleep(s)

    # start of generated code
    def list_templates(self, language: Language = "en") -> list[TemplateInfo]:
        """List all available templates in format name.language."""
        r = self._request("GET", "/templates", params={"lang": language})
        return [TemplateInfo(**template) for template in r.json()]

    def get_user_info(self, user: str = "me") -> UserInfo:
        """Request stored information and credit balance of a given user."""
        r1 = self._request("GET", f"/users/{user}")
        r2 = self._request("GET", f"/users/{user}/credits")
        return UserInfo(**r1.json(), **r2.json())

    def list_user_jobs(
        self,
        user: str = "me",
        *,
        limit: int | None = None,
        offset: int | None = None,
        errors_only: bool | None = None,
    ) -> Page[JobInfo]:
        """List all a user's jobs with their duration and status.

        A job started whenever a document is passed throuh a pipeline.
        """
        r = self._request(
            "GET",
            f"/users/{user}/jobs",
            params=drop_none(limit=limit, offset=offset, errors_only=errors_only),
        )
        return Page[JobInfo].from_response(r)

    def set_user_credits(
        self,
        user: str,
        *,
        billing_scheme: Optional[BillingScheme] = None,
        new_credits: Optional[int] = None,
        balance: Optional[int] = None,
    ) -> None:
        """Set billing information for a user.

        billing_scheme ... a user can be billed "by_invoice" or "per_page"

        If the user is billed "per_page", they will consume
        one credit of their balance per processed page.

        Then Smartextract admins can either:

        new_credits ... add new credits to existing balance
        balance ... reset balance to new value

        """
        self._request(
            "PATCH",
            f"/users/{user}/credits",
            json=drop_none(
                billing_scheme=billing_scheme,
                new_credits=new_credits,
                balance=balance,
            ),
        )

    def list_resources(
        self,
        type: str | None = None,  # noqa: A002
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[IdInfo]:
        """List the ids of all the users resources.

        The user can create resources of type
        ["inbox", "template_pipeline", "lua_pipeline"]

        The user can use resources of type ["aws-ocr", "openai-chat, "anthropic-chat"]
        as input to the creation methods.

        """
        r = self._request(
            "GET",
            "/resources",
            params=drop_none(
                type=type,
                limit=limit,
                offset=offset,
            ),
        )
        return Page[IdInfo].from_response(r)

    def list_lua_pipelines(
        self, limit: int | None = None, offset: int | None = None
    ) -> Page[IdInfo]:
        """List the ids of all the users lua_pipelines.

        Pipelines can be started with a lua script
        by using create_lua_pipeline(...)
        """
        return self.list_resources(type="lua_pipeline", limit=limit, offset=offset)

    def list_template_pipelines(
        self, limit: int | None = None, offset: int | None = None
    ) -> Page[IdInfo]:
        """List all created pipelines that are based on a template."""
        return self.list_resources(type="template_pipeline", limit=limit, offset=offset)

    def list_inboxes(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[IdInfo]:
        """List all inboxes with the attached pipeline.

        order_by must be one of "id", "name", "date".
        """
        r = self._request(
            "GET",
            "/inboxes",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[IdInfo].from_response(r)

    def list_documents(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[DocumentInfo]:
        """List all documents inside an inbox.

        order_by must be one of ["id", "name", "date"]
        """
        r = self._request(
            "GET",
            f"/inboxes/{inbox_id}/documents",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[DocumentInfo].from_response(r)

    def get_resource_info(self, resource_id: ResourceID) -> ResourceInfo:
        """Get various information about a given resource.

        Information includes the resource type, name, access level,
        and additional details specific to the resource type.
        """
        r = self._request("GET", f"/resources/{resource_id}")
        info = r.json()
        if info["type"] == "lua_pipeline":
            r = self._request("GET", f"/pipelines/{resource_id}")
            return LuaPipelineInfo.from_response(r)
        if info["type"] == "template_pipeline":
            r = self._request("GET", f"/pipelines/{resource_id}")
            return TemplatePipelineInfo.from_response(r)
        if info["type"] == "inbox":
            r = self._request("GET", f"/inboxes/{resource_id}")
            return InboxInfo.from_response(r)
        return ResourceInfo(**info)

    def list_permissions(
        self,
        resource_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[UserPermission]:
        """For a given resource, list all users with access rights."""
        r = self._request(
            "GET",
            f"/resources/{resource_id}/permissions",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[UserPermission].from_response(r)

    def create_permission(
        self, resource_id: ResourceID, user: str, level: AccessLevel
    ) -> None:
        """Allow user access to a resource."""
        self._request(
            "POST",
            f"/resources/{resource_id}/permissions",
            json={"user": user, "level": level},
        )

    def create_lua_pipeline(
        self,
        name: str,
        code: str,
        *,
        permissions: Optional[dict[str, AccessLevel]] = None,
    ) -> UUID:
        """Create a new pipeline by providing a lua script.

        To run the pipeline for a PDF-document use run_pipeline(..)

        In the lua script's scope the PDF is available by the variable
        "document", which is an Iterator of Pages.
        """
        r = self._request(
            "POST",
            "/pipelines",
            json=drop_none(name=name, code=code, permissions=permissions),
        )
        return UUID(r.json()["id"])

    def create_template_pipeline(
        self,
        name: str,
        template: Union[str, dict],
        *,
        chat_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
        permissions: Optional[dict[str, AccessLevel]] = None,
        use_vision: Optional[bool] = None,
    ) -> UUID:
        """Create a new pipeline based on a yaml-template.

        template ... consult the docs: https://docs.smartextract.ai/guide/pipelines/#templates

        chat_id ... must be of resource type "openai-chat" or "anthropic-chat"
        ocr_id ... must be of resource type "aws-ocr"

        """
        r = self._request(
            "POST",
            "/pipelines",
            json=drop_none(
                name=name,
                template=template,
                chat_id=chat_id,
                ocr_id=ocr_id,
                permissions=permissions,
                use_vision=use_vision,
            ),
        )
        return UUID(r.json()["id"])

    def modify_pipeline(
        self,
        pipeline_id: ResourceID,
        *,
        name: Optional[str] = None,
        code: Optional[str] = None,
        template: Union[None, str, dict] = None,
        chat_id: Optional[ResourceID] = None,
        location_chat_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
        use_vision: Optional[bool] = None,
    ) -> None:
        """Change details of an existing pipeline.

        Provide a new Lua script (code) for a Lua pipeline, or provide
        a new template, chat_id, ocr_id or use_vision attribute for a
        template pipeline.
        """
        self._request(
            "PATCH",
            f"/pipelines/{pipeline_id}",
            json=drop_none(
                name=name,
                code=code,
                template=template,
                chat_id=chat_id,
                location_chat_id=location_chat_id,
                ocr_id=ocr_id,
                use_vision=use_vision,
            ),
        )

    def run_pipeline(
        self,
        pipeline_id: ResourceID,
        document: Document,
        *,
        media_type: str | None = None,
    ) -> JobResult:
        """Process a document through an existing pipeline.

        With this method, it is not necessary to upload the document
        to an inbox.  The document and the resulting extraction are
        not persisted in the smartextract servers.

        This method waits for the processing to complete and directly
        returns the extracted data.

        Arguments:
          pipeline_id: The processing pipeline to use.
          document: The document to be processed, as a string, bytes,
            or a file in binary reading mode.
          media_type: The document media type, only required when it
            is not possible to guess.
        """
        filename = _guess_filename(document) or "document"
        media_type = media_type or _guess_media_type(filename)
        r = self._request(
            "POST",
            f"/pipelines/{pipeline_id}/run",
            files={"document": (filename, document, media_type)},
        )
        return JobResult.from_response(r)

    def run_anonymous_pipeline(
        self,
        document: Document,
        *,
        code: str | None = None,
        template: dict | None = None,
        media_type: str | None = None,
    ) -> JobResult:
        """Process a document without permanently creating a pipeline.

        This is useful for debugging.  Either Lua code or an
        extraction template (but not both) need to be provided.

        As with `run_pipeline`, the document and the resulting
        extraction are not persisted in the smartextract servers.

        Arguments:
          document: The document to be processed, as a string, bytes,
            or a file in binary reading mode.
          code: A Lua script, as a string.
          template: An extraction template as a dictionary following
            the schema at https://smartextract.ai/schemas/template.
          media_type: The document media type, only required when it
            is not possible to guess.
        """
        if code is None:
            if template is None:
                raise ValueError("Either code or template must be provided")
            code = json.dumps(template)
            code_type = "application/json"
        elif template is None:
            code_type = "text/lua"
        else:
            raise ValueError("Only one of code or template must be provided")

        filename = _guess_filename(document) or "document"
        media_type = media_type or _guess_media_type(filename)
        r = self._request(
            "POST",
            "/pipelines/run",
            files={
                "document": (filename, document, media_type),
                "code": ("code", code, code_type),
            },
        )
        return JobResult.from_response(r)

    def list_pipeline_jobs(
        self,
        pipeline_id: Optional[ResourceID],
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[JobInfo]:
        """List all pipeline runs of a pipeline."""
        r = self._request(
            "GET",
            f"/pipelines/{pipeline_id}/jobs",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[JobInfo].from_response(r)

    def create_inbox(
        self, name: str, pipeline_id: str, *, ocr_id: Optional[str] = None
    ) -> UUID:
        """Create container for storing documents of common type.

        Inbox must be set up with document-type specific extraction pipeline.
        """
        r = self._request(
            "POST",
            "/inboxes",
            json=drop_none(name=name, pipeline_id=pipeline_id, ocr_id=ocr_id),
        )
        return UUID(r.json()["id"])

    def modify_inbox(
        self,
        inbox_id: ResourceID,
        *,
        name: Optional[str] = None,
        pipeline_id: Optional[ResourceID] = None,
        ocr_id: Optional[ResourceID] = None,
    ) -> None:
        """Set new pipeline for an inbox."""
        self._request(
            "PATCH",
            f"/inboxes/{inbox_id}",
            json=drop_none(
                name=name,
                pipeline_id=pipeline_id,
                ocr_id=ocr_id,
            ),
        )

    def list_inbox_jobs(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[JobInfo]:
        """List all a inbox' pipeline runs."""
        r = self._request(
            "GET",
            f"/inboxes/{inbox_id}/jobs",
            params=drop_none(limit=limit, offset=offset),
        )
        return Page[JobInfo].from_response(r)

    def create_document(
        self,
        inbox_id: ResourceID,
        document: Document,
        *,
        filename: str | None = None,
        media_type: str | None = None,
    ) -> UUID:
        """Add a new document to an existing inbox.

        Return the ID of the newly created document.

        Arguments:
          inbox_id: The inbox in which to add a document.
          document: The contents of new document, as a string, bytes,
            or a file in binary reading mode.
          filename: The new document's name.  This can be omitted if
            `document` is a file, in which case the file's name is
            used.
          media_type: The new document's type.  This can be omitted if
            the type can be deduced from the file name.
        """
        filename = filename or _guess_filename(document)
        if not filename:
            raise ValueError("File name needs to be specified.")

        if not media_type:
            media_type, enc = MimeTypes().guess_type(filename)
            if enc is not None:
                raise ValueError(f"Encoded file ({enc}) is not supported.")

        r = self._request(
            "POST",
            f"/inboxes/{inbox_id}",
            files={"document": (filename, document, media_type)},
        )
        return UUID(r.json()["id"])

    def list_extractions(
        self,
        inbox_id: ResourceID,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = "date:desc",
    ) -> Page[ExtractionInfo]:
        """List all extraction results of an inbox.

        order_by must be one of ["id", "name", "date"]
        """
        r = self._request(
            "GET",
            f"inboxes/{inbox_id}/extractions",
            params=drop_none(limit=limit, offset=offset, order_by=order_by),
        )
        return Page[ExtractionInfo].from_response(r)

    def get_document_info(self, document_id: ResourceID) -> DocumentInfo:
        """Get name, access level and inbox location for a given document id."""
        r = self._request("GET", f"/documents/{document_id}")
        return DocumentInfo.from_response(r)

    def delete_document(self, document_id: ResourceID) -> None:
        """Delete document from database."""
        self._request("DELETE", f"/documents/{document_id}")

    def get_document_bytes(self, document_id: ResourceID) -> bytes:
        """Get document content in bytes."""
        r = self._request("GET", f"/documents/{document_id}/blob")
        return r.content

    def get_document_extraction(
        self, document_id: ResourceID, *, recompute: bool = False
    ) -> ExtractionInfo:
        """Get the document extraction from its latest pipeline processing."""
        if recompute:
            r = self._request(
                "POST",
                f"/documents/{document_id}/extraction",
                params={"recompute": True},
            )
            if not r.is_success:
                raise ClientError.from_response(r)
        r = self._request(
            "GET",
            f"/documents/{document_id}/extraction",
        )
        return ExtractionInfo.from_response(r)

    def set_document_extraction(
        self, document_id: ResourceID, extraction: JsonValue
    ) -> None:
        """Manually override the extraction data of the given document."""
        self._request("POST", f"/documents/{document_id}/extraction", json=extraction)

    def create_dataset_item(self, dataset_id: ResourceID, key: str, value: JsonValue):
        """Add item to a dataset."""
        key = url_quote(key)
        self._request("POST", f"/datasets/{dataset_id}/items/{key}", json=value)

    def delete_dataset_item(self, dataset_id: ResourceID, key: str):
        """Add item to a dataset."""
        key = url_quote(key)
        self._request("DELETE", f"/datasets/{dataset_id}/items/{key}")

    # end of generated code
