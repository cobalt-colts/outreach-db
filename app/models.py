from pydantic import BaseModel
from pydantic import Field as APIField
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class LoginModel(SQLModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(SQLModel):
    id: int
    email: str
    permission_level: int
    first_name: str
    last_name: str
    team_number: int


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("permission_level >= 0", name="users_permission_level_check"),
    )

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=320)
    password_argon2: str
    permission_level: int = Field(default=0, ge=0)
    first_name: str
    last_name: str
    team_number: int


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    __table_args__ = (
        UniqueConstraint("name", "city", "state", name="unique_organization"),
        CheckConstraint(
            "status IN ('active', 'archived', 'flagged')",
            name="organizations_status_check",
        ),
        CheckConstraint(
            "audit_status IN ('checked', 'corrected')",
            name="organizations_audit_status_check",
        ),
        CheckConstraint(
            "audit_status <> 'corrected' OR audit_notes IS NOT NULL",
            name="audit_notes_required_when_corrected",
        ),
        CheckConstraint(
            "length(state) = 2 AND state = upper(state)",
            name="organizations_state_check",
        ),
        CheckConstraint(
            "zip_code GLOB '[0-9][0-9][0-9][0-9][0-9]'",
            name="organizations_zip_code_check",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str
    city: str = Field(index=True)
    state: str = Field(index=True, min_length=2, max_length=2)
    # TEXT, never an int: 145 CSV rows have a leading-zero ZIP ("04330").
    zip_code: str = Field(min_length=5, max_length=5)
    description: str
    link: str
    audit_status: str = Field(default="checked")
    audit_notes: str | None = None
    verified_by: str | None = None
    verified_at: str | None = None
    status: str = Field(default="active")


class OrganizationTag(SQLModel, table=True):
    __tablename__ = "organization_tags"
    __table_args__ = (
        UniqueConstraint("organization_id", "tag", name="unique_organization_tags"),
    )

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(
        foreign_key="organizations.id",
        ondelete="CASCADE",
        index=True,
    )
    tag: str

class OrganizationAPI(BaseModel):
    """Request body for creating an organization; mirrors the v5 CSV columns."""

    name: str = APIField(min_length=1)
    city: str = APIField(min_length=1)
    state: str = APIField(pattern=r"^[A-Z]{2}$")
    zip_code: str = APIField(pattern=r"^[0-9]{5}$")
    description: str = APIField(min_length=1)
    link: str = APIField(min_length=1)
    tags: list[str] = []


class OrganizationRead(BaseModel):
    """Response shape for organization reads, with tags folded in."""

    id: int
    name: str
    city: str
    state: str
    zip_code: str
    description: str
    link: str
    audit_status: str
    audit_notes: str | None
    status: str
    tags: list[str]