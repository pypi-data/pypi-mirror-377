from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from pytz import utc


@dataclass
class Flag:
    name: str
    value: bool
    desc: str | None = None
    expiration_date: datetime | None = None
    date_created: datetime = field(default_factory=lambda: datetime.now(tz=utc))
    date_updated: datetime = field(default_factory=lambda: datetime.now(tz=utc))

    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def expired(self) -> bool:
        return bool(self.expiration_date and self.expiration_date <= datetime.now(tz=utc))
