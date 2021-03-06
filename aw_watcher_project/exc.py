class ConfigException(Exception):
    pass


class CannotAddProjectException(ConfigException):
    pass


class CannotRemoveProjectException(ConfigException):
    pass


class ProjectDoesNotExistException(ValueError):
    pass