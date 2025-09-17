from typing import Protocol

from src.domain.flag import Flag


class FlagsShipRepo(Protocol):
    async def store(self, flag: Flag) -> None:
        """
        Store a new Flag in the repository.
        """
        raise NotImplementedError

    async def get_by_id(self, _id: str) -> Flag | None:
        """
        Retrieve a Flag by its ID from the repository.
        """
        raise NotImplementedError

    async def get_by_name(self, name: str) -> Flag | None:
        """
        Retrieve a Flag by its name from the repository.
        """
        raise NotImplementedError

    async def get_all(self, limit: int = 100) -> list[Flag]:
        """
        Retrieve all Flags from the repository, up to the specified limit.
        """
        raise NotImplementedError

    async def update(self, flag: Flag) -> bool:
        """
        Update an existing Flag in the repository.
        """
        raise NotImplementedError

    async def delete(self, _id: str) -> bool:
        """
        Delete a Flag by its ID from the repository.
        """
        raise NotImplementedError
