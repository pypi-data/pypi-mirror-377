from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.boolean import OptionalBoolean


HierarchyT = TypeVar("HierarchyT", bound=OptionalBoolean)


class IsRoot(BaseModel, Generic[HierarchyT]):
    is_root: HierarchyT = Field(..., description="Whether is root")


class IsParent(BaseModel, Generic[HierarchyT]):
    is_parent: HierarchyT = Field(..., description="Whether is parent")


class IsChild(BaseModel, Generic[HierarchyT]):
    is_child: HierarchyT = Field(..., description="Whether is child")


class IsLeaf(BaseModel, Generic[HierarchyT]):
    is_leaf: HierarchyT = Field(..., description="Whether is leaf")
