# This file was generated automatically. Do not edit it directly.
from typing import List, Literal, NotRequired, TypedDict, Union, Unpack, cast
from urllib.parse import quote

from fountain_life_service_clients._base_client import (
    AlphaConfig,
    AlphaResponse,
    BaseClient,
)


class ListTemplatesParams(TypedDict):
    prefix: NotRequired[str]
    pageSize: NotRequired[float]
    nextPageToken: NotRequired[str]


class Items(TypedDict):
    type: Literal["folder"]
    path: str


class items(TypedDict):
    type: Literal["template"]
    path: str
    description: NotRequired[str]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    impressionType: NotRequired[
        Literal[
            "brain",
            "cancer",
            "heart",
            "metabolic",
            "musculoskeletal",
            "nutrition",
            "overview",
            "synopsis",
            "supplements",
            "general",
        ]
    ]
    lastUpdatedBy: str


class Items2(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    lastUpdatedBy: str


class Links(TypedDict):
    next: NotRequired[str]


class ListTemplatesResponse(TypedDict):
    items: List[Union[Items, items, Items2]]
    links: Links


class CreateTemplateRequest1(TypedDict):
    type: Literal["template"]
    path: str
    description: NotRequired[str]
    content: str


class Section(TypedDict):
    templateId: str


class CreateTemplateRequest2(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    sections: List[Section]


CreateTemplateRequest = Union[CreateTemplateRequest1, CreateTemplateRequest2]


class Template(TypedDict):
    type: Literal["template"]
    path: str
    description: NotRequired[str]
    content: str
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    impressionType: NotRequired[
        Literal[
            "brain",
            "cancer",
            "heart",
            "metabolic",
            "musculoskeletal",
            "nutrition",
            "overview",
            "synopsis",
            "supplements",
            "general",
        ]
    ]
    lastUpdatedBy: str


class template(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    sections: List[Section]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    lastUpdatedBy: str


class CreateTemplateResponse(TypedDict):
    template: Union[Template, template]


class Template2(TypedDict):
    """
    The template or composite report definition
    """

    type: Literal["template"]
    path: str
    description: NotRequired[str]
    content: str
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    impressionType: NotRequired[
        Literal[
            "brain",
            "cancer",
            "heart",
            "metabolic",
            "musculoskeletal",
            "nutrition",
            "overview",
            "synopsis",
            "supplements",
            "general",
        ]
    ]
    lastUpdatedBy: str


class Template3(TypedDict):
    """
    The template or composite report definition
    """

    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    sections: List[Section]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    lastUpdatedBy: str


class GetTemplateResponse(TypedDict):
    template: Union[Template2, Template3]


class PatchTemplateRequest1(TypedDict):
    type: Literal["template"]
    path: NotRequired[str]
    description: NotRequired[str]
    content: NotRequired[str]


class PatchTemplateRequest2(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: NotRequired[str]
    description: NotRequired[str]
    sections: NotRequired[List[Section]]


PatchTemplateRequest = Union[PatchTemplateRequest1, PatchTemplateRequest2]


class Template4(TypedDict):
    type: Literal["template"]
    path: str
    description: NotRequired[str]
    content: str
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    impressionType: NotRequired[
        Literal[
            "brain",
            "cancer",
            "heart",
            "metabolic",
            "musculoskeletal",
            "nutrition",
            "overview",
            "synopsis",
            "supplements",
            "general",
        ]
    ]
    lastUpdatedBy: str


class Template5(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    sections: List[Section]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    lastUpdatedBy: str


class PatchTemplateResponse(TypedDict):
    template: Union[Template4, Template5]


class DeleteTemplateResponse(TypedDict):
    pass


class CopyTemplateRequest(TypedDict):
    path: NotRequired[str]


class Template6(TypedDict):
    type: Literal["template"]
    path: str
    description: NotRequired[str]
    content: str
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    impressionType: NotRequired[
        Literal[
            "brain",
            "cancer",
            "heart",
            "metabolic",
            "musculoskeletal",
            "nutrition",
            "overview",
            "synopsis",
            "supplements",
            "general",
        ]
    ]
    lastUpdatedBy: str


class Template7(TypedDict):
    type: Literal["compositeReportDefinition"]
    path: str
    description: NotRequired[str]
    sections: List[Section]
    id: str
    accountId: str
    createdAt: str
    updatedAt: str
    lastUpdatedBy: str


class CopyTemplateResponse(TypedDict):
    template: Union[Template6, Template7]


class AiTemplateServiceClient(BaseClient):
    def __init__(self, **cfg: Unpack[AlphaConfig]):
        kwargs = {"target": "lambda://ai-template-service:deployed", **(cfg or {})}
        super().__init__(**kwargs)

    async def list_templates(self, params: ListTemplatesParams):
        """Lists all templates and folders, matching against an optional prefix."""
        res = await self.client.request(
            path="/v1/ai-templates", method="GET", params=cast(dict, params)
        )
        return cast(AlphaResponse[ListTemplatesResponse], res)

    async def create_template(self, body: CreateTemplateRequest):
        """Creates a new template. Returns the created template, or 409 if a template already exists under the given path."""
        res = await self.client.request(
            path="/v1/ai-templates", method="POST", body=cast(dict, body)
        )
        return cast(AlphaResponse[CreateTemplateResponse], res)

    async def get_template(self, id: str):
        """Gets a template by ID. Returns 404 if the template does not exist."""
        res = await self.client.request(
            path=f"/v1/ai-templates/{quote(id)}", method="GET"
        )
        return cast(AlphaResponse[GetTemplateResponse], res)

    async def patch_template(self, id: str, body: PatchTemplateRequest):
        """Patches a template. Any keys present in the input will be updated. Returns the patched template."""
        res = await self.client.request(
            path=f"/v1/ai-templates/{quote(id)}", method="PATCH", body=cast(dict, body)
        )
        return cast(AlphaResponse[PatchTemplateResponse], res)

    async def delete_template(self, id: str):
        """Deletes a template, if it exists."""
        res = await self.client.request(
            path=f"/v1/ai-templates/{quote(id)}", method="DELETE"
        )
        return cast(AlphaResponse[DeleteTemplateResponse], res)

    async def copy_template(self, id: str, body: CopyTemplateRequest):
        """Copies a template."""
        res = await self.client.request(
            path=f"/v1/ai-templates/{quote(id)}/copy",
            method="POST",
            body=cast(dict, body),
        )
        return cast(AlphaResponse[CopyTemplateResponse], res)
