"""Pydantic schemas for User."""

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    preferred_language: str = "en"


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
