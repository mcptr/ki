class Error(Exception):
    pass


class ValidationError(Error):
    pass


class AuthenticationError(Error):
    pass


class AuthorizationError(Error):
    pass


class DatabaseError(Error):
    pass
