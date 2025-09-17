from pydantic import BaseModel, ConfigDict, Field

from elrahapi.authorization.base_meta_model import MetaAuthorizationBaseModel
from elrahapi.utility.schemas import AdditionalSchemaFields


class RolePrivilegeCreateModel(BaseModel):
    role_id: int = Field(example=1)
    privilege_id: int = Field(example=2)
    is_active: bool = Field(exemple=True, default=True)


class RolePrivilegePatchModel(BaseModel):
    role_id: int | None = Field(example=1, default=None)
    privilege_id: int | None = Field(example=2, default=None)
    is_active: bool | None = Field(exemple=True, default=None)


class RolePrivilegeUpdateModel(BaseModel):
    role_id: int = Field(example=1)
    privilege_id: int = Field(example=2)
    is_active: bool = Field(exemple=True)


class RolePrivilegeReadModel(RolePrivilegeCreateModel, AdditionalSchemaFields):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RolePrivilegeFullReadModel(BaseModel, AdditionalSchemaFields):
    id: int
    role: MetaAuthorizationBaseModel
    privilege: MetaAuthorizationBaseModel
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
