from dataclasses import dataclass


@dataclass(slots=True)
class UserSession:
    username: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.username is not None

    def start(self, username: str) -> None:
        self.username = username

    def clear(self) -> None:
        self.username = None
