from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import (
    CurrentUserResponse,
    OutreachEvent,
    OutreachEventAPI,
    OutreachEventResponse,
    OutreachEventTag,
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

def create_event(session: Session, event_api: OutreachEventAPI) -> OutreachEvent:
    """Create an outreach event and its associated tags in one transaction."""
    event = OutreachEvent(**event_api.model_dump(exclude={"tags"}))

    try:
        session.add(event)
        session.flush()

        if event.id is None:
            raise RuntimeError("The created event did not receive an ID.")

        session.add_all(
            OutreachEventTag(event_id=event.id, tag=tag)
            for tag in dict.fromkeys(event_api.tags)
        )
        session.commit()
        session.refresh(event)
    except Exception:
        session.rollback()
        raise

    return event

def get_events(session: Session) -> list[OutreachEventResponse]:
    """Fetch all events with their associated tags."""
    events = session.exec(select(OutreachEvent)).all()
    result = []
    
    for event in events:
        tags_rows = session.exec(
            select(OutreachEventTag).where(OutreachEventTag.event_id == event.id)
        ).all()
        tags = [tag.tag for tag in tags_rows]
        
        result.append(OutreachEventResponse(
            id=event.id or 0,
            name=event.name,
            location=event.location,
            description=event.description,
            link=event.link,
            tags=tags
        ))
    
    return result

def get_event(session: Session, event_id: int) -> OutreachEventResponse | None:
    """Fetch a single event with its associated tags."""
    event = session.exec(select(OutreachEvent).where(OutreachEvent.id == event_id)).first()
    
    if event is None:
        return None
    
    tags_rows = session.exec(
        select(OutreachEventTag).where(OutreachEventTag.event_id == event.id)
    ).all()
    tags = [tag.tag for tag in tags_rows]
    
    return OutreachEventResponse(
        id=event.id or 0,
        name=event.name,
        location=event.location,
        description=event.description,
        link=event.link,
        tags=tags
    )
