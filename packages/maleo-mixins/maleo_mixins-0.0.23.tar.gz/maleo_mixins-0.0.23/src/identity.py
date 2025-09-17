from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union
from uuid import UUID as PythonUUID, uuid4
from maleo.types.integer import OptionalInteger, OptionalListOfIntegers
from maleo.types.string import OptionalString, OptionalListOfStrings
from maleo.types.uuid import OptionalUUID, OptionalListOfUUIDs


IdentifierTypeT = TypeVar("IdentifierTypeT", bound=StrEnum)


class IdentifierType(BaseModel, Generic[IdentifierTypeT]):
    identifier: IdentifierTypeT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class IdentifierTypeValue(
    IdentifierValue[IdentifierValueT],
    IdentifierType[IdentifierTypeT],
    BaseModel,
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


IdT = TypeVar(
    "IdT",
    bound=Union[
        OptionalInteger,
        OptionalUUID,
    ],
)


class Id(BaseModel, Generic[IdT]):
    id: IdT = Field(..., description="ID")


IdsT = TypeVar("IdsT", bound=Union[OptionalListOfIntegers, OptionalListOfUUIDs])


class Ids(BaseModel, Generic[IdsT]):
    ids: IdsT = Field(..., description="Ids")


IntIdT = TypeVar("IntIdT", bound=OptionalInteger)


class IntId(BaseModel, Generic[IntIdT]):
    id: IntIdT = Field(..., ge=1, description="Id (Integer)")


IntIdsT = TypeVar("IntIdsT", bound=OptionalListOfIntegers)


class IntIds(BaseModel, Generic[IntIdsT]):
    ids: IntIdsT = Field(..., description="Ids (Integers)")


UUIDT = TypeVar("UUIDT", bound=OptionalUUID)


class UUIDId(BaseModel, Generic[UUIDT]):
    id: UUIDT = Field(..., description="Id (UUID)")


class OperationId(UUIDId[PythonUUID]):
    id: PythonUUID = Field(default_factory=uuid4, description="Operation's ID")


class RequestId(UUIDId[PythonUUID]):
    id: PythonUUID = Field(default_factory=uuid4, description="Request's ID")


UUIDsT = TypeVar("UUIDsT", bound=OptionalListOfUUIDs)


class UUIDIds(BaseModel, Generic[UUIDsT]):
    ids: UUIDsT = Field(..., description="Ids (UUIDs)")


class UUID(BaseModel, Generic[UUIDT]):
    uuid: UUIDT = Field(..., description="UUID")


class UUIDs(BaseModel, Generic[UUIDsT]):
    uuids: UUIDsT = Field(..., description="UUIDs")


class DataIdentifier(
    UUID[PythonUUID],
    IntId[int],
):
    id: int = Field(..., ge=1, description="Data's ID")


KeyT = TypeVar("KeyT", bound=OptionalString)


class Key(BaseModel, Generic[KeyT]):
    key: KeyT = Field(..., description="Key")


KeysT = TypeVar("KeysT", bound=OptionalListOfStrings)


class Keys(BaseModel, Generic[KeysT]):
    keys: KeysT = Field(..., description="Keys")


NameT = TypeVar("NameT", bound=OptionalString)


class Name(BaseModel, Generic[NameT]):
    name: NameT = Field(..., description="Name")


NamesT = TypeVar("NamesT", bound=OptionalListOfStrings)


class Names(BaseModel, Generic[NamesT]):
    names: NamesT = Field(..., description="Names")


OrganizationIdT = TypeVar("OrganizationIdT", bound=OptionalInteger)


class OrganizationId(BaseModel, Generic[OrganizationIdT]):
    organization_id: OrganizationIdT = Field(..., ge=1, description="Organization's ID")


OrganizationIdsT = TypeVar("OrganizationIdsT", bound=OptionalListOfIntegers)


class OrganizationIds(BaseModel, Generic[OrganizationIdsT]):
    organization_ids: OrganizationIdsT = Field(..., description="Organization's IDs")


ParentIdT = TypeVar("ParentIdT", bound=OptionalInteger)


class ParentId(BaseModel, Generic[ParentIdT]):
    parent_id: ParentIdT = Field(..., ge=1, description="Parent's ID")


ParentIdsT = TypeVar("ParentIdsT", bound=OptionalListOfIntegers)


class ParentIds(BaseModel, Generic[ParentIdsT]):
    parent_ids: ParentIdsT = Field(..., description="Parent's IDs")


UserIdT = TypeVar("UserIdT", bound=OptionalInteger)


class UserId(BaseModel, Generic[UserIdT]):
    user_id: UserIdT = Field(..., ge=1, description="User's ID")


UserIdsT = TypeVar("UserIdsT", bound=OptionalListOfIntegers)


class UserIds(BaseModel, Generic[UserIdsT]):
    user_ids: UserIdsT = Field(..., description="User's IDs")
