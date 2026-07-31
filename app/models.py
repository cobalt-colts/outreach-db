from sqlalchemy import CheckConstraint
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


class OutreachEvent(SQLModel, table=True):
    __tablename__ = "outreach_events"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    location: str
    description: str
    link: str


class OutreachEventTag(SQLModel, table=True):
    __tablename__ = "outreach_event_tags"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(
        foreign_key="outreach_events.id",
        ondelete="CASCADE",
        index=True,
    )
    tag: str
