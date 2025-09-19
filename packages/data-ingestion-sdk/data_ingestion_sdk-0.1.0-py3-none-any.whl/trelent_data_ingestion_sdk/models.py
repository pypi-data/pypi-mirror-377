from __future__ import annotations

from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


# ---- Connector inputs (mirrors API schema) ----


class S3KeysConnector(BaseModel):
    type: Literal["s3"]
    bucket_name: str
    object_keys: List[str]


class S3PrefixConnector(BaseModel):
    type: Literal["s3_prefix"]
    bucket_name: str
    prefix: str


class UrlConnector(BaseModel):
    type: Literal["url"]
    urls: List[str]


Connector = Annotated[
    Union[S3KeysConnector, S3PrefixConnector, UrlConnector],
    Field(discriminator="type"),
]


# ---- Output definitions (mirrors API schema) ----


class BucketOutput(BaseModel):
    type: Literal["bucket"]
    bucket_name: str
    prefix: str


class S3SignedUrlOutput(BaseModel):
    type: Literal["s3-signed-url"]
    expires_minutes: int = 1440


Output = Annotated[
    Union[BucketOutput, S3SignedUrlOutput],
    Field(discriminator="type"),
]


class JobInput(BaseModel):
    connector: Connector
    output: Output
    force_error: Optional[bool] = False


# ---- Responses (mirrors API schema) ----


class WorkflowSummary(BaseModel):
    type: str
    namespace: str
    uid: str
    name: Optional[str] = None
    generate_name: Optional[str] = None
    submitted: bool


class ProcessResponse(BaseModel):
    submitted: bool
    errors: List[str]
    workflows: List[WorkflowSummary]
    job_id: Optional[UUID] = None


class JobStatusItem(BaseModel):
    uid: str
    phase: str
    name: Optional[str] = None
    namespace: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class BucketPointer(BaseModel):
    bucket: str
    key: str


class S3SignedUrlDeliveryItem(BaseModel):
    images: Dict[str, HttpUrl]
    markdown_delivery: Union[HttpUrl, BucketPointer]
    markdown: Optional[str] = None


class BucketDeliveryItem(BaseModel):
    images: Dict[str, BucketPointer]
    markdown_delivery: BucketPointer
    markdown: Optional[str] = None


DeliveryItem = Union[S3SignedUrlDeliveryItem, BucketDeliveryItem]


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    workflows: List[JobStatusItem]
    delivery: Optional[Dict[str, DeliveryItem]] = None
    errors: Optional[Dict[str, List[str]]] = None

    model_config = ConfigDict(extra="allow")


class HealthzResponse(BaseModel):
    status: str


