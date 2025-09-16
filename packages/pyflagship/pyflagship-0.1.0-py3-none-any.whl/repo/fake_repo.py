from src.domain.flag import Flag


class FakeInMemoryRepo:
    def __init__(self) -> None:
        self.mem_store: dict[str, Flag] = {}

    async def store(self, flag: Flag) -> None:
        """
        Store a new Flag in the repository.
        """
        self.mem_store[flag.id] = flag

    async def get_by_id(self, _id: str) -> Flag | None:
        """
        Retrieve a Flag by its ID from the repository.
        """
        return self.mem_store.get(_id)

    async def get_by_name(self, name: str) -> Flag | None:
        """
        Retrieve a Flag by its name from the repository.
        """
        for flag in self.mem_store.values():
            if flag.name == name:
                return flag
        return None

    async def get_all(self, limit: int = 100) -> list[Flag]:
        """
        Retrieve all Flags from the repository, up to the specified limit.
        """
        return list(self.mem_store.values())[:limit]

    async def update(self, flag: Flag) -> bool:
        """
        Update an existing Flag in the repository.
        """
        if flag.id in self.mem_store:
            self.mem_store[flag.id] = flag
            return True
        return False

    async def delete(self, _id: str) -> bool:
        """
        Delete a Flag by its ID from the repository.
        """
        if _id in self.mem_store:
            del self.mem_store[_id]
            return True
        return False
