"""Manage configuration files and settings."""

from typing import Any, Optional, Union

from collections import UserDict
from enum import Enum
from pathlib import Path

from dynaconf import Dynaconf, DynaconfFormatError, DynaconfParseError, ValidationError
from dynaconf.base import Settings
from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList
from dynaconf.vendor.tomllib import TOMLDecodeError
from tomlkit import dump as toml_dump

from dynamanager.exceptions import (
    DomainNotFoundError,
    DuplicateConfigError,
    DuplicateSettingFileError,
    InnerKeyError,
    InvalidConfigFileError,
    NonExistingConfigFileError,
    SettingNotFoundError,
)
from dynamanager.utils import resolve_dot_notation_accessor


class AccessorMode(Enum):
    """Flag handler for using bracket notation with Dynamanager objects."""

    GET = True
    SET = False


class ConfigContainer(UserDict):  # type: ignore[type-arg]
    """Wrap Dynaconf objects inside a UserDict."""

    MAX_KEY_LENGTH = 2

    def __init__(self, data=None):
        super().__init__(data)

    def _validate_accessor_keys(
        self, keys: Union[str, tuple[Optional[str]]], mode: AccessorMode
    ) -> tuple[str, Optional[str]]:
        if isinstance(keys, str):
            config_name, setting_key = resolve_dot_notation_accessor(keys)

        elif len(keys) > self.MAX_KEY_LENGTH:
            len_msg = (
                "ConfigContainer objects accept only up to two keys for indexing. Use "
                '`object["config_name", "setting"]` or `object["config_name.setting"]` '
                "instead"
            )

            raise KeyError(len_msg)

        else:
            config_name, setting_key = keys  # type: ignore[misc]

        self._resolve_called_index(config_name, setting_key, mode)

        return config_name, setting_key

    def _resolve_called_index(
        self, config_name: str, settings_key: Optional[str], getter_method: AccessorMode
    ) -> None:
        if getter_method.value and settings_key is not None:  # noqa: SIM102
            if self.data[config_name].get(settings_key) is None:
                setting_msg = (
                    f"setting '{settings_key}' does not exist in configuration "
                    f"'{config_name}'"
                )

                raise KeyError(setting_msg)

    def __getitem__(
        self, keys: Union[str, tuple[str]]
    ) -> Union[Dynaconf, DynaBox, BoxList, str, int, float, bool]:
        """Allow dictionary-style access."""
        config_name, setting_key = self._validate_accessor_keys(
            keys, mode=AccessorMode.GET
        )

        try:
            config = self.data[config_name]

        except KeyError as err:
            raise DomainNotFoundError(config_name) from err

        else:
            if setting_key is None:
                return config

            return config[setting_key]

    def __setitem__(
        self,
        keys: Union[str, tuple[str]],
        value: Union[Dynaconf, dict[str, Any], list[Any], str, int, float, bool],
    ) -> None:
        """Allow dictionary-style assignment."""
        config_name, setting_key = self._validate_accessor_keys(
            keys, mode=AccessorMode.SET
        )

        if setting_key is None and not isinstance(value, (Dynaconf, Settings)):
            msg = "ConfigContainer objects only allow Dynaconf instances for storage"
            raise KeyError(msg)

        if setting_key is None:
            self.data[config_name] = value

        else:
            self.data[config_name].set(setting_key, value)

    def __contains__(self, name: str) -> bool:  # type: ignore[override]
        """Support the `in` operator."""
        return name in self.data

    def __bool__(self) -> bool:
        """Return True if there are any configuration domains defined."""
        return bool(self.data)

    @property
    def empty(self) -> bool:
        """Check if container is empty when no configuration domains are defined."""
        return len(self.data) == 0

    def remove(self, name: str) -> None:
        """Remove an object from the container.

        Parameter
        ---------
        name : str
            Key in the `data` dictionary to be removed.

        Raises
        ------
        DomainNotFoundError
            If the configuration domain does not exist.
        """
        try:
            self.data.pop(name)

        except KeyError as err:
            raise DomainNotFoundError(name) from err


class Dynamanager:
    """Manage multiple separate Dynaconf instances and their respective files."""

    def __init__(
        self,
        config_definitions: Optional[dict[str, dict[str, Any]]] = None,
        base_dir: Optional[Union[str, Path]] = None,
        default_contents: Optional[dict[str, Any]] = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the manager.

        Parameters
        ----------
        config_definitions : dict
            Dictionary mapping the config names to `Dynaconf` kwargs for instatiation.
        base_dir : str, Path, optional
            Base directory to fetch and store configuration files. If not provided, will
            use the current working directory.
        default_contents : dict, optional
            Default contents for configuration files if they do not exist.
        **kwargs
            Keyword arguments defining config names and receiving a dictionary with
            `Dynaconf` kwargs for instatiation. If provided, will take precedence over
            `config_definitions`.
        """
        self._configs = ConfigContainer()
        self._originals: dict[str, dict[str, Any]] = {}
        self._default_config = default_contents or {}
        self.base_config_dir = Path(base_dir) if base_dir else Path.cwd()

        definition_mappings = config_definitions or {}
        config_parser = definition_mappings | kwargs

        for name, config_kwargs in config_parser.items():
            self.add(name, **config_kwargs)

    def _validate_settings_file_argument(
        self,
        domain_name: str,
        dynaconf_files_argument: Optional[
            Union[str, Path, list[Union[str, Path]], tuple[Union[str, Path]]]
        ],
        dynaconf_file_argument: Optional[
            Union[str, Path, list[Union[str, Path]], tuple[Union[str, Path]]]
        ],
    ) -> Path:
        msg = "Dynamanager only accepts one configuration file per domain"

        if dynaconf_files_argument is not None and dynaconf_file_argument is not None:
            raise DuplicateSettingFileError(msg)

        provided_arg = dynaconf_files_argument or dynaconf_file_argument

        if provided_arg is None:
            resolved_file = Path(f"{domain_name}.toml")

        if isinstance(provided_arg, (str, Path)):
            resolved_file = Path(provided_arg)

        if isinstance(provided_arg, (list, tuple)):
            if len(provided_arg) > 1:
                raise DuplicateSettingFileError(msg)

            resolved_file = Path(provided_arg[0])

        return resolved_file

    def _validate_dynaconf_constructor(
        self, domain_name: str, args: dict[str, Any]
    ) -> dict[str, Any]:
        validated_args = args.copy()

        settings_files = validated_args.get("settings_files")
        settings_file = validated_args.get("settings_file")

        config_file = self._validate_settings_file_argument(
            domain_name, settings_files, settings_file
        )

        resolved_path = self._resolve_path(config_file)
        validated_args.pop("settings_files", None)
        validated_args.pop("settings_file", None)
        validated_args["settings_file"] = resolved_path

        validated_args.setdefault("envvar_prefix", domain_name.upper())
        validated_args["core_loaders"] = ["TOML"]

        return validated_args

    def _resolve_path(self, file_path: Union[str, Path]) -> Path:
        path = Path(file_path).expanduser()

        return path if path.is_absolute() else self.base_config_dir / path

    def _add_config(
        self,
        domain_name: str,
        **dynaconf_kwargs: Union[bool, list[str], str, dict[str, Any], Path, None],
    ) -> None:
        named_attribute = domain_name.lower()

        load_kwargs = self._validate_dynaconf_constructor(
            named_attribute, dynaconf_kwargs
        )
        config_file = load_kwargs["settings_file"]

        try:
            added_config = Dynaconf(**load_kwargs)
            added_config.to_dict()  # Required to catch errors with invalid TOML syntax

        except (DynaconfFormatError, DynaconfParseError, ValidationError) as error:
            msg = f"failed to load config from {config_file}: {error}"

            raise InvalidConfigFileError(msg) from error

        except TOMLDecodeError as error:
            msg = f"invalid TOML syntax in {config_file}: {error}"

            raise InvalidConfigFileError(msg) from error

        except Exception as error:
            msg = (
                "unknown error while attempting to load config from "
                f"{config_file}: {error}"
            )

            raise InvalidConfigFileError(msg) from error

        else:
            if not Path(config_file).exists():
                self._save_config(self._default_config, added_config.settings_file)
                added_config.reload()

            self._configs[named_attribute] = added_config
            self._update_original_state(named_attribute)

            setattr(self, named_attribute, added_config)

    def _save_config(self, data: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup_file = path.with_suffix(".toml.bak")

        for file_path in [path, backup_file]:
            with file_path.open("w") as toml_file:
                toml_dump(data, toml_file)

    def save(self, config_domain: str) -> None:
        """Save a configuration domain, persisting any changes at runtime.

        config_domain : str
            Name of the configuration domain to save.
        """
        to_save = self._configs[config_domain]

        self._save_config(to_save.to_dict(), to_save.settings_file)  # type: ignore[union-attr]
        self._update_original_state(config_domain)

    def save_all(self):
        """Save all configuration domains to TOML settings files at once."""
        for config in self._configs:
            self.save(config)

    def reload(self, config_domain: str) -> None:
        """Reload a configuration domain, discarding any changes made at runtime.

        Parameter
        ---------
        config_domain : str
            Name of the configuration domain to reload.
        """
        self._configs[config_domain].configure()  # type: ignore[union-attr]

    def reload_all(self) -> None:
        """Reload all configuration domains at once."""
        for config in self._configs.values():
            self.reload(config)

    def _update_original_state(self, config_domain: str) -> None:
        self._originals[config_domain] = self._configs[config_domain].to_dict()  # type: ignore[union-attr]

    def add(
        self,
        domain_name: str,
        custom_config: Optional[Union[str, Path]] = None,
        **dynaconf_kwargs: Optional[Union[str, bool, Path, list[Any], dict[str, Any]]],
    ) -> None:
        """Add a new configuration domain to manage.

        The added config will be accessible through the `name` attribute.

        Parameters
        ----------
        domain_name : str
            User-defined name of the configuration domain. Will be used to access the
            config from the manager via attribute.
        custom_config : str, Path, optional
            Path to the desired configuration file to be loaded. If not provided, will
            define the path to be used based on `name`. When provided, the file must
            exist in the filesystem, otherwise will raise a
            `NonExistingConfigFileError`.
        **dynaconf_kwargs : dict
            Arguments to be passed to the `Dynaconf` constructor to instantiate a
            config. If not provided, the manager will define the `settings_file` and
            `envvar_prefix` arguments based on `name`.
        """
        if domain_name in self._configs:
            msg = f"configuration '{domain_name}' already exists"
            raise DuplicateConfigError(msg)

        if custom_config is not None:
            config_path = Path(custom_config)

            self._validate_custom_config(domain_name, config_path)
            dynaconf_kwargs["settings_file"] = config_path

        self._add_config(domain_name, **dynaconf_kwargs)

    def _validate_custom_config(self, domain_name: str, config_path: Path) -> None:
        if config_path.suffix != ".toml":
            msg = f'"{config_path}" is not a TOML file; only TOML files are accepted'

            raise InvalidConfigFileError(msg)

        if not config_path.exists():
            raise NonExistingConfigFileError(domain_name, config_path)

    def get(self, key: str) -> Union[Dynaconf, DynaBox, BoxList, str, int, float, bool]:
        """Get an item by dot notation. Will return None if key is not found.

        Parameter
        ---------
        key : str
            Dot-notation string to get the item.
        """
        try:
            return self[key]

        except KeyError:
            return None

    def set(
        self, key: str, value: Union[dict[str, Any], list[Any], str, int, float, bool]
    ) -> None:
        """Define or modify a setting in a configuration domain.

        Parameters
        ----------
        key : str
            Dot-notation string to set the item.
        value : dict, list, str, int, float, bool
            Value to be set.

        Raises
        ------
        KeyError
            This method can only set values inside a configuration domain. Attempting to
            set the configuration domain itself will raise this exception. Use the `add`
            method instead to include new domains in the manager instance.
        """
        self[key] = value

    def remove_config(self, config_domain: str) -> None:
        """Remove a configuration domain from the manager.

        Parameter
        ---------
        config_domain : str
            Name of the configuration domain to remove.

        Raises
        ------
        DomainNotFoundError
            If the configuration domain does not exist.
        """
        if config_domain in self._configs:
            self._configs.remove(config_domain)

            if hasattr(self, config_domain):
                delattr(self, config_domain)

        else:
            raise DomainNotFoundError(config_domain)

    def unset(self, key: str) -> None:
        """Remove an item from the manager.

        Parameter
        ---------
        key : str
            Dot-notation string to fetch the item. If a single-level key is provided,
            will look for a configuration domain to remove. Otherwise will attempt
            removing a setting from the specified configuration domain.

        Raises
        ------
        SettingNotFoundError
            When attempting to remove an entire configuration domain which does not
            exist.
        InnerKeyError
            Dynaconf objects only allow for top-level keys to be removed. If an inner
            key is provided when calling this method, Dynamanager will not block the
            attempted operation.
        """
        config, *setting = resolve_dot_notation_accessor(key, depth=2)

        if len(setting) == 0:
            self.remove_config(config)

        elif len(setting) == 1:
            top_level_key = setting[0]
            config_object = self._configs[config]

            if top_level_key not in config_object:  # type: ignore[operator]
                raise SettingNotFoundError(config, top_level_key)  # type: ignore[arg-type]

            config_object.unset(top_level_key)  # type: ignore[union-attr]

        else:
            setting_str = ".".join(setting)  # type: ignore[arg-type]
            msg = (
                f"Dynaconf settings can only unset top-level keys, got '{setting_str}' "
                "instead"
            )
            raise InnerKeyError(msg)

    def list_configs(self) -> list[str]:
        """List all available configuration domains."""
        return list(self._configs.keys())

    def __getitem__(
        self, keys: Union[str, tuple[str]]
    ) -> Union[Dynaconf, DynaBox, BoxList, str, int, float, bool]:
        """Allow dictionary-style access with a single dot-notation key or two keys."""
        return self._configs[keys]

    def __setitem__(
        self,
        keys: Union[str, tuple[str]],
        value: Union[dict[str, Any], list[Any], str, int, float, bool],
    ) -> None:
        """Define or modify a setting in a configuration domain."""
        config_name, setting_key = resolve_dot_notation_accessor(keys)  # type: ignore[arg-type]

        if setting_key is None:
            msg = "cannot modify configuration domains directly"
            raise KeyError(msg)

        self._configs[keys] = value

    def __contains__(self, name: str) -> bool:
        """Support the `in` operator."""
        return name in self._configs

    def __repr__(self) -> str:  # pragma: no cover
        """Return a string representation for a manager with basic information."""
        configs = ", ".join(self._configs.keys())
        default_config = bool(self._default_config)

        return (
            f"Dynamanager(configs=[{configs}], "
            f"base_dir='{self.base_config_dir}', uses_default_config={default_config})"
        )

    def __bool__(self) -> bool:
        """Return True if there are any configuration domains defined."""
        return bool(self._configs)

    @property
    def empty(self) -> bool:
        """Check if manager is empty when no configuration domains are defined."""
        return self._configs.empty
