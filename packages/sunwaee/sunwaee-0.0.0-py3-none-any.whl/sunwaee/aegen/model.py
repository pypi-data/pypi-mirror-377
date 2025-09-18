# standard
# third party
# custom


class Model:
    def __init__(
        self, name: str, display_name: str, origin: str, version: str | None = None
    ):
        self.name = name
        self.display_name = display_name
        self.origin = origin
        self.version = version
