from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, col, create_engine, select

from app.models import (
    CurrentUserResponse,
    Organization,
    OrganizationAPI,
    OrganizationRead,
    OrganizationTag,
    User,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"


def create_db_engine(db_path: str | Path = DEFAULT_DB_PATH) -> Engine:
    database = Path(db_path).resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    db_engine = create_engine(
        f"sqlite:///{database.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(db_engine, "connect")
    def enable_foreign_keys(
        dbapi_connection: Any, _connection_record: Any
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return db_engine


engine = create_db_engine()


def init_db(db_engine: Engine = engine) -> None:
    """Create any missing SQLModel tables without modifying existing data."""
    SQLModel.metadata.create_all(db_engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def get_user(session: Session, uid: int) -> CurrentUserResponse | None:
    """Return public user fields; the password hash is never returned."""
    user = session.exec(select(User).where(User.id == uid)).first()
    return CurrentUserResponse.model_validate(user) if user is not None else None

def get_user_from_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def update_password_hash(session: Session, user: User, password_hash: str) -> None:
    user.password_argon2 = password_hash
    session.add(user)
    session.commit()

def create_event(session: Session, event_api: OrganizationAPI) -> Organization:
    """Create an organization and its associated tags in one transaction."""
    event = Organization(**event_api.model_dump(exclude={"tags"}))

    try:
        session.add(event)
        session.flush()

        if event.id is None:
            raise RuntimeError("The created organization did not receive an ID.")

        session.add_all(
            OrganizationTag(organization_id=event.id, tag=tag)
            for tag in dict.fromkeys(event_api.tags)
        )
        session.commit()
        session.refresh(event)
    except Exception:
        session.rollback()
        raise

    return event

def _tags_by_organization(
    session: Session, organization_ids: list[int]
) -> dict[int, list[str]]:
    """Fetch tags for many organizations in one query, keyed by organization id."""
    if not organization_ids:
        return {}

    rows = session.exec(
        select(OrganizationTag.organization_id, OrganizationTag.tag).where(
            col(OrganizationTag.organization_id).in_(organization_ids)
        )
    ).all()

    tags: dict[int, list[str]] = {oid: [] for oid in organization_ids}
    for organization_id, tag in rows:
        tags[organization_id].append(tag)
    return tags


def _to_read_model(organization: Organization, tags: list[str]) -> OrganizationRead:
    return OrganizationRead(
        **organization.model_dump(exclude={"verified_by", "verified_at"}), tags=tags
    )


def get_events(session: Session) -> list[OrganizationRead]:
    organizations = list(session.exec(select(Organization)).all())
    tags = _tags_by_organization(
        session, [o.id for o in organizations if o.id is not None]
    )
    return [_to_read_model(o, tags.get(o.id or -1, [])) for o in organizations]


def get_event(session: Session, event_id: int) -> OrganizationRead | None:
    organization = session.exec(
        select(Organization).where(Organization.id == event_id)
    ).first()
    if organization is None or organization.id is None:
        return None

    tags = _tags_by_organization(session, [organization.id])
    return _to_read_model(organization, tags[organization.id])
