"""Exceptions for Dynamanager."""

from pathlib import Path


class NonExistingConfigFileError(Exception):
    def __init__(self, config_name: str, settings_file_path: Path):
        super().__init__(
            f"custom file \"{settings_file_path}\" provided for '{config_name}' "
            "configuration domain does not exist"
        )


class InvalidConfigFileError(Exception):
    pass


class InnerKeyError(Exception):
    pass


class DomainNotFoundError(KeyError):
    def __init__(self, config_name: str):
        super().__init__(f"configuration domain '{config_name}' does not exist")


class SettingNotFoundError(KeyError):
    def __init__(self, config_name: str, setting: str):
        super().__init__(f"setting key '{setting}' not found in domain '{config_name}'")


class DuplicateSettingFileError(ValueError):
    pass


class DuplicateConfigError(ValueError):
    pass
