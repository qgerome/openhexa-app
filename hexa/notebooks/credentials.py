import base64


class NotebooksCredentialsError(Exception):
    pass


class NotebooksCredentials:
    """This class acts as a container for credentials to be provided to the notebooks component."""

    def __init__(self, user):
        self.user = user
        self.env: dict[str, str] = {}
        self.files: dict[str, bytes] = {}

    @property
    def authenticated(self):
        return self.user.is_authenticated

    def update_env(self, env_dict):
        self.env.update(**env_dict)

    def to_dict(self):
        return {
            "username": self.user.email,
            "env": self.env,
            "files": {k: base64.b64encode(v).decode() for k, v in self.files.items()},
        }
