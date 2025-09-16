from pydantic import BaseModel, Field
from typing import Dict, Generic, Optional, TypeVar, Union
from maleo.mixins.general import Success, Descriptor, Other


OptionalMetadataT = TypeVar("OptionalMetadataT", bound=Optional[BaseModel])


class MetadataMixin(BaseModel, Generic[OptionalMetadataT]):
    metadata: OptionalMetadataT = Field(..., description="Metadata")


class FieldExpansionMetadata(Other, Descriptor[str], Success[bool]):
    pass


class FieldExpansionMetadataMixin(BaseModel):
    field_expansion: Optional[Union[str, Dict[str, FieldExpansionMetadata]]] = Field(
        None, description="Field expansion metadata"
    )
