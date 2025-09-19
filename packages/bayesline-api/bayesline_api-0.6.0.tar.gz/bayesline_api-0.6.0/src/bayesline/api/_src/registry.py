from __future__ import annotations

import abc
import datetime as dt
import re
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, ValidationError

from bayesline.api._src._utils import docstrings_from_sync


class InvalidSettingsError(ValueError):
    """Exception raised when settings are invalid."""

    pass


class Settings(BaseModel, frozen=True, extra="forbid"):
    """Base class for all settings objects."""

    def references(
        self,
    ) -> dict[str, dict[type[Settings], list[str | int]]]:
        """
        Get all other settings that are referenced by this settings.

        For example, if a risk model references a universe.

        Returns
        -------
        dict[str, dict[type[Settings], list[str | int]]]
            A dict of the field name to a dict of the referenced settings type to the list
            of referenced settings (either by name or id).
        """
        result: dict[str, dict[type[Settings], list[str | int]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for field_name, field_info in self.__class__.model_fields.items():
            for meta_data in field_info.metadata:
                if isinstance(meta_data, SettingsTypeMetaData):
                    ref_type = meta_data.references
                    field_value = getattr(self, field_name)
                    if field_value is not None:
                        result[field_name][ref_type].extend(
                            meta_data.extract(field_value)
                        )

        return result

    def get_references(self) -> Sequence[str | int]:
        """
        Get references for this settings object.

        Returns
        -------
        Sequence[str | int]
            A sequence of references (strings or integers) for this settings object.
        """
        return []


E = TypeVar("E")


@dataclass
class SettingsTypeMetaData(Generic[E]):
    """Metadata for settings type references."""

    references: type[Settings]
    # a function that extracts only the references from the settings
    extractor: Callable[[E], list[str | int]] | None = None

    def extract(self, v: E) -> list[str | int]:
        """
        Extract references from a value.

        Parameters
        ----------
        v : E
            The value to extract references from.

        Returns
        -------
        list[str | int]
            A list of extracted references.

        Raises
        ------
        ValueError
            If the value type cannot be extracted and no extractor is defined.
        """
        if self.extractor is None:
            if isinstance(v, str | int):
                return [v]
            elif isinstance(v, self.references):
                return []
            else:
                raise ValueError(
                    f"Cannot extract {v} of type {type(v)}. "
                    "Define an extractor in the pydantic model"
                )
        return self.extractor(v)


class RawSettings(BaseModel):
    """Raw settings data structure."""

    model_type: str
    name: str | None
    identifier: int | None
    exists: bool
    raw_json: dict[str, Any]
    references: list[RawSettings]
    extra: dict[str, Any] = Field(default_factory=dict)


T = TypeVar("T")
SettingsType = TypeVar("SettingsType", bound=Settings)
ModelType = str


class AsyncSettingsResolver(abc.ABC):
    """Abstract base class for async settings resolvers."""

    @classmethod
    @abc.abstractmethod
    def model_types(cls) -> dict[ModelType, type[Settings]]:
        """
        Get model types mapping.

        Returns
        -------
        dict[ModelType, type[Settings]]
            A dictionary of the model types (str) to their type instance.
            Typically this is e.g. `{UniverseSettings.__name__: UniverseSettings}`.
        """

    @abc.abstractmethod
    async def resolve_settings(self, settings: list[Settings]) -> list[RawSettings]:
        """
        Resolve the given references.

        Parameters
        ----------
        settings : list[Settings]
            The settings to resolve.

        Returns
        -------
        list[RawSettings]
            List of raw settings exactly in the same order as the input.
        """

    @abc.abstractmethod
    async def resolve_references(
        self, references: list[tuple[ModelType, str | int]]
    ) -> list[RawSettings]:
        """
        Resolve the given settings references.

        Parameters
        ----------
        references : list[tuple[ModelType, str | int]]
            The settings references to resolve.

        Returns
        -------
        list[RawSettings]
            List of raw settings exactly in the same order as the input.
        """

    async def to_settings_model(
        self, raw_settings: RawSettings, resolve: bool = False
    ) -> Settings:
        """
        Convert the given raw settings to a settings model.

        Parameters
        ----------
        raw_settings : RawSettings
            The raw settings to convert.
        resolve : bool, default=False
            If True, the references are resolved.

        Returns
        -------
        Settings
            The settings model.

        Raises
        ------
        InvalidSettingsError
            If the raw settings are invalid.
        NotImplementedError
            If resolve=True is not implemented.
        """
        if resolve:
            # resolve all references recursively
            raise NotImplementedError()
        if not await self.is_valid(raw_settings):
            raise InvalidSettingsError(raw_settings.raw_json)
        return self.model_types()[raw_settings.model_type].model_validate(
            raw_settings.raw_json
        )

    async def is_valid(self, raw_setting: RawSettings) -> bool:
        """
        Check if the given raw settings are valid.

        Parameters
        ----------
        raw_setting : RawSettings
            The raw settings to check.

        Returns
        -------
        bool
            True if the raw setting is valid, False otherwise.
        """
        valid = raw_setting.exists
        valid &= not self.is_corrupted(raw_setting)
        valid &= await self.has_all_references(raw_setting)

        if valid:
            settings_model = self.model_types()[raw_setting.model_type].model_validate(
                raw_setting.raw_json
            )
            valid &= not (await self.errors_against_settings_menu(settings_model))
        return valid

    def is_corrupted(self, raw_setting: RawSettings) -> bool:
        """
        Check if the given raw settings are corrupted.

        Parameters
        ----------
        raw_setting : RawSettings
            The raw settings to check.

        Returns
        -------
        bool
            True if the raw setting is corrupted, False otherwise.
        """
        if not raw_setting.raw_json:
            return True

        try:
            settings_type = self.model_types()[raw_setting.model_type]
            settings_type.model_validate(raw_setting.raw_json)
            return False
        except ValidationError:
            return True
        except KeyError:
            return True

    async def has_all_references(self, raw_settings: RawSettings) -> bool:
        """
        Check if the given settings have all their references.

        Parameters
        ----------
        raw_settings : RawSettings
            The raw settings to check.

        Returns
        -------
        bool
            True if the settings have all their references, False otherwise.
        """
        return all([await self.is_valid(ref) for ref in raw_settings.references])

    @abc.abstractmethod
    async def errors_against_settings_menu(self, settings: Settings) -> list[str]:
        """
        Get errors that the given settings have against the settings menu.

        Parameters
        ----------
        settings : Settings
            The settings to validate.

        Returns
        -------
        list[str]
            A list of error messages if the settings are invalid against the settings menu.
        """

    async def validation_messages(self, raw_settings: RawSettings) -> list[str]:
        """
        Get validation messages for raw settings.

        Parameters
        ----------
        raw_settings : RawSettings
            The raw settings to get validation messages for.

        Returns
        -------
        list[str]
            A list of validation messages for the raw settings.
        """
        messages = []
        corrupted = self.is_corrupted(raw_settings)
        missing = not raw_settings.exists
        if missing:
            messages.append("The setting does not exist.")
        elif corrupted:
            messages.append("The setting json is invalid.")
        if not missing and not corrupted:
            await self.errors_against_settings_menu(
                self.model_types()[raw_settings.model_type].model_validate(
                    raw_settings.raw_json
                )
            )
            messages.extend(
                (
                    await self.errors_against_settings_menu(
                        self.model_types()[raw_settings.model_type].model_validate(
                            raw_settings.raw_json
                        )
                    )
                )
            )
        for ref in raw_settings.references:
            ref_messages = [
                m.replace("The setting", f"The reference {ref.name!r}")
                for m in await self.validation_messages(ref)
            ]
            messages.extend(ref_messages)
        return messages


class SettingsMetaData(BaseModel, frozen=True, extra="allow"):
    """Metadata for settings objects."""

    created_on: dt.datetime
    last_updated: dt.datetime


class SettingsMenu(
    abc.ABC,
    BaseModel,
    Generic[SettingsType],
    frozen=True,
    extra="forbid",
):
    """Abstract base class for settings menus."""

    @abc.abstractmethod
    def describe(self, settings: SettingsType | None = None) -> str:
        """
        Describe the settings menu.

        Parameters
        ----------
        settings : SettingsType | None, default=None
            The settings to describe.
            If None, then the description is not evaluated against any settings.

        Returns
        -------
        str
            A human readable description of the settings menu,
            optionally evaluated against the given settings.
        """

    @abc.abstractmethod
    def validate_settings(self, settings: SettingsType) -> None:
        """
        Validate if the given settings are valid for this settings menu.

        Parameters
        ----------
        settings : SettingsType
            The settings to validate.

        Raises
        ------
        ValidationError
            If a pydantic error occurs.
        ValueError
            If passed settings values are invalid.
        """


SettingsMenuType = TypeVar("SettingsMenuType", bound=SettingsMenu)


class EmptySettingsMenu(SettingsMenu[SettingsType]):
    """Empty settings menu implementation."""

    def describe(self, settings: SettingsType | None = None) -> str:
        """
        Describe the empty settings menu.

        Parameters
        ----------
        settings : SettingsType | None, default=None
            The settings to describe. If None, returns a default description.

        Returns
        -------
        str
            A description of the empty settings menu or the settings in JSON format.
        """
        if settings is not None:
            return settings.model_dump_json(indent=2)
        return "EmptySettingsMenu"

    def validate_settings(self, settings: SettingsType) -> None:
        """
        Validate settings against the empty menu.

        Parameters
        ----------
        settings : SettingsType
            The settings to validate.

        Returns
        -------
        None
            This method always succeeds as the empty menu accepts all settings.
        """
        settings.__class__.model_validate(settings.model_dump())


Mode = Literal["All", "Valid", "Invalid"]


class ReadOnlyRegistry(abc.ABC, Generic[T]):
    """Abstract base class for read-only registries."""

    @abc.abstractmethod
    def ids(self, mode: Mode = "Valid") -> dict[int, str]:
        """
        Get mapping of IDs to names.

        Parameters
        ----------
        mode : Mode, default="Valid"
            The mode to use when retrieving the ids.

        Returns
        -------
        dict[int, str]
            A dictionary of the unique identifiers to the unique names.
        """

    @abc.abstractmethod
    def names(self, mode: Mode = "Valid") -> dict[str, int]:
        """
        Get mapping of names to IDs.

        Parameters
        ----------
        mode : Mode, default="Valid"
            The mode to use when retrieving the names.

        Returns
        -------
        dict[str, int]
            A dictionary of the unique names to the unique identifiers.
        """

    @abc.abstractmethod
    def get_raw(self, name_or_id: list[str | int]) -> list[RawSettings]:
        """
        Get raw settings by names or IDs.

        Parameters
        ----------
        name_or_id : list[str | int]
            The unique names or int identifiers of the items to retrieve.

        Returns
        -------
        list[RawSettings]
            A list of `RawSettings` in the same order as input.
        """

    @abc.abstractmethod
    def get(self, name: str | int) -> T:
        """
        Get an item by name or ID.

        Parameters
        ----------
        name : str | int
            The unique name or int identifier of the item to retrieve.

        Raises
        ------
        KeyError
            If the item does not exist.
        InvalidSettingsError
            If the item exists but is invalid.

        Returns
        -------
        T
            The item for the given name.
        """

    @abc.abstractmethod
    def get_metadata(self, name: str | int) -> SettingsMetaData:
        """
        Get metadata for an item by name or ID.

        Parameters
        ----------
        name : str | int
            The unique name or int identifier of the item to retrieve.

        Raises
        ------
        KeyError
            If the item does not exist.

        Returns
        -------
        SettingsMetaData
            The metadata for the given name.
        """

    def get_all(self) -> dict[str, T]:
        """
        Get all valid available settings.

        Returns
        -------
        dict[str, T]
            A dictionary of all valid available settings.
        """
        return {name: self.get(name) for name in self.names()}

    def get_all_with_metadata(self) -> dict[str, tuple[T, SettingsMetaData]]:
        """
        Get all valid available settings with metadata.

        Returns
        -------
        dict[str, tuple[T, SettingsMetaData]]
            A dictionary of all valid available settings with metadata.
        """
        all_settings = self.get_all()
        all_metadata = self.get_all_metadata()

        return {
            name: (all_settings[name], all_metadata[name])
            for name in all_settings.keys()
        }

    def get_all_metadata(self) -> dict[str, SettingsMetaData]:
        """
        Get all available settings metadata.

        Returns
        -------
        dict[str, SettingsMetaData]
            A dictionary of all available settings metadata (valid or invalid).
        """
        return {name: self.get_metadata(name) for name in self.names()}


class Registry(Generic[T], ReadOnlyRegistry[T]):
    """Abstract base class for writable registries."""

    @abc.abstractmethod
    def save(self, name: str, settings: T) -> int:
        """
        Save an item to the registry.

        Parameters
        ----------
        name : str
            The unique name of the item to save.
            The name cannot be all numbers.
        settings : T
            The item to save.

        Raises
        ------
        ValueError
            If the item name already exists or is all numbers.

        Returns
        -------
        int
            A unique identifier for the saved item.
        """

    @abc.abstractmethod
    def update(self, name: str | int, settings: T) -> RawSettings:
        """
        Update an existing item in the registry.

        Parameters
        ----------
        name : str | int
            The unique name or int identifier of the item to update.
        settings : T
            The item to update.

        Raises
        ------
        KeyError
            If the item does not exist.

        Returns
        -------
        RawSettings
            The previous raw settings item for the given name.
        """

    @abc.abstractmethod
    def delete(self, name: str | int) -> RawSettings:
        """
        Delete an item from the registry.

        Parameters
        ----------
        name : str | int
            The unique name or int identifier of the settings to delete.

        Raises
        ------
        KeyError
            If the item does not exist.

        Returns
        -------
        RawSettings
            The deleted raw settings item for the given name.
        """


@docstrings_from_sync
class AsyncReadOnlyRegistry(abc.ABC, Generic[T]):

    @abc.abstractmethod
    async def ids(self, mode: Mode = "Valid") -> dict[int, str]: ...  # noqa: D102

    @abc.abstractmethod
    async def names(self, mode: Mode = "Valid") -> dict[str, int]: ...  # noqa: D102

    @abc.abstractmethod
    async def get_raw(  # noqa: D102
        self, name_or_id: list[str | int]
    ) -> list[RawSettings]: ...

    @abc.abstractmethod
    async def get(self, name: str | int) -> T: ...  # noqa: D102

    @abc.abstractmethod
    async def get_metadata(self, name: str | int) -> SettingsMetaData: ...  # noqa: D102

    async def get_all(self) -> dict[str, T]:  # noqa: D102
        return {name: await self.get(name) for name in await self.names()}

    async def get_all_with_metadata(  # noqa: D102
        self,
    ) -> dict[str, tuple[T, SettingsMetaData]]:
        all_settings = await self.get_all()
        all_metadata = await self.get_all_metadata()

        return {
            name: (all_settings[name], all_metadata[name])
            for name in all_settings.keys()
        }

    async def get_all_metadata(self) -> dict[str, SettingsMetaData]:  # noqa: D102
        return {name: await self.get_metadata(name) for name in await self.names()}


class AsyncRegistry(Generic[T], AsyncReadOnlyRegistry[T]):
    """Abstract base class for async writable registries."""

    @abc.abstractmethod
    async def save(self, name: str, settings: T) -> int: ...  # noqa: D102

    @abc.abstractmethod
    async def update(  # noqa: D102
        self, name: str | int, settings: T
    ) -> RawSettings: ...

    @abc.abstractmethod
    async def delete(self, name: str | int) -> RawSettings: ...  # noqa: D102


class SettingsRegistry(Registry[SettingsType], Generic[SettingsType, SettingsMenuType]):
    """Registry for settings with validation against a settings menu."""

    @abc.abstractmethod
    def available_settings(self, dataset_name: str | None = None) -> SettingsMenuType:
        """
        Get available settings menu for this registry.

        Parameters
        ----------
        dataset_name : str | None, default=None
            The name of the dataset to use when retrieving the settings menu.
            If not provided, the settings menu will be retrieved for the
            default dataset.

        Returns
        -------
        SettingsMenuType
            A description of valid settings for this registry.
        """

    def save(self, name: str, settings: SettingsType) -> int:
        """
        Save settings with validation.

        Parameters
        ----------
        name : str
            The name for the settings.
        settings : SettingsType
            The settings to save.

        Returns
        -------
        int
            The unique identifier for the saved settings.

        Raises
        ------
        ValueError
            If the name consists only of numbers or if validation fails.
        """
        if re.sub(r"\d", "", name) == "":
            raise ValueError(
                f"The model model name cannot consist of only numbers: {name}",
            )
        # TODO not ideal to do a hasattr check here. think of more robust way.
        if hasattr(settings, "dataset"):
            dataset_name = settings.dataset
        else:
            dataset_name = None
        self.available_settings(dataset_name).validate_settings(settings)
        return self._do_save(name, settings)

    @abc.abstractmethod
    def _do_save(self, name: str, settings: SettingsType) -> int: ...

    def update(self, name: str | int, settings: SettingsType) -> RawSettings:
        """
        Update settings with validation.

        Parameters
        ----------
        name : str | int
            The name or identifier of the settings to update.
        settings : SettingsType
            The new settings to update with.

        Returns
        -------
        RawSettings
            The previous raw settings before the update.

        Raises
        ------
        ValueError
            If validation fails.
        """
        # TODO not ideal to do a hasattr check here. think of more robust way.
        if hasattr(settings, "dataset"):
            dataset_name = settings.dataset
        else:
            dataset_name = None
        self.available_settings(dataset_name).validate_settings(settings)
        return self._do_update(name, settings)

    @abc.abstractmethod
    def _do_update(self, name: str | int, settings: SettingsType) -> RawSettings: ...


@docstrings_from_sync
class AsyncSettingsRegistry(
    AsyncRegistry[SettingsType], Generic[SettingsType, SettingsMenuType]
):

    @abc.abstractmethod
    async def available_settings(  # noqa: D102
        self, dataset_name: str | None = None
    ) -> SettingsMenuType: ...

    async def save(self, name: str, settings: SettingsType) -> int:  # noqa: D102
        if re.sub(r"\d", "", name) == "":
            raise ValueError(
                f"The model model name cannot consist of only numbers: {name}",
            )
        if name in await self.names():
            raise ValueError(f"Name {name} already exists.")

        # TODO not ideal to do a hasattr check here. think of more robust way.
        if hasattr(settings, "dataset"):
            dataset_name = settings.dataset
        else:
            dataset_name = None

        (await self.available_settings(dataset_name)).validate_settings(settings)
        return await self._do_save(name, settings)

    @abc.abstractmethod
    async def _do_save(self, name: str, settings: SettingsType) -> int: ...

    async def update(  # noqa: D102
        self, name: str | int, settings: SettingsType
    ) -> RawSettings:
        # TODO not ideal to do a hasattr check here. think of more robust way.
        if hasattr(settings, "dataset"):
            dataset_name = settings.dataset
        else:
            dataset_name = None
        (await self.available_settings(dataset_name)).validate_settings(settings)
        return await self._do_update(name, settings)

    @abc.abstractmethod
    async def _do_update(
        self, name: str | int, settings: SettingsType
    ) -> RawSettings: ...


# has no sync version so no @docstrings_from_sync
class AsyncInMemorySettingsRegistry(
    AsyncSettingsRegistry[SettingsType, SettingsMenuType]
):
    """In-memory async settings registry implementation.

    Parameters
    ----------
    model_type : type[SettingsType]
        The type of settings this registry will store.
    settings_menu : Callable[[str | None], Awaitable[SettingsMenuType]] | SettingsMenuType
        The settings menu or a callable that returns it.
    resolver : AsyncSettingsResolver
        The resolver for resolving settings references.
    """

    def __init__(
        self,
        model_type: type[SettingsType],
        settings_menu: (
            Callable[[str | None], Awaitable[SettingsMenuType]] | SettingsMenuType
        ),
        resolver: AsyncSettingsResolver,
    ):
        self._model_type = model_type
        self._settings_menu = settings_menu
        self._resolver = resolver

        self._settings: dict[int, SettingsType] = {}
        self._metadata: dict[int, SettingsMetaData] = {}
        self._id_name_map: dict[int, str] = {}
        self._name_id_map: dict[str, int] = {}
        self._next_id = 0

    async def ids(self, mode: Mode = "Valid") -> dict[int, str]:
        """
        Get mapping of IDs to names.

        Parameters
        ----------
        mode : Mode, default="Valid"
            The mode to use when retrieving the ids.

        Returns
        -------
        dict[int, str]
            A dictionary of the unique identifiers to the unique names.

        Raises
        ------
        ValueError
            If an unknown mode is specified.
        """
        all_ids = dict(self._id_name_map)
        if mode == "All":
            return all_ids
        elif mode in {"Valid", "Invalid"}:
            all_settings: list[Settings] = [self._settings[i] for i in all_ids]
            resolved = await self._resolver.resolve_settings(all_settings)
            for identifier, resolved_setting in zip(
                list(all_ids), resolved, strict=True
            ):
                valid = await self._resolver.is_valid(resolved_setting)
                if mode == "Valid" and not valid:
                    all_ids.pop(identifier)
                elif mode == "Invalid" and valid:
                    all_ids.pop(identifier)
            return all_ids
        else:
            raise ValueError(f"Unknown mode: {mode}")

    async def names(self, mode: Mode = "Valid") -> dict[str, int]:
        """
        Get mapping of names to IDs.

        Parameters
        ----------
        mode : Mode, default="Valid"
            The mode to use when retrieving the names.

        Returns
        -------
        dict[str, int]
            A dictionary of the unique names to the unique identifiers.

        Raises
        ------
        ValueError
            If an unknown mode is specified.
        """
        all_names = dict(self._name_id_map)
        if mode == "All":
            return all_names
        elif mode in {"Valid", "Invalid"}:
            all_settings: list[Settings] = [
                self._settings[self._name_id_map[n]] for n in all_names
            ]
            resolved = await self._resolver.resolve_settings(all_settings)
            for name, resolved_setting in zip(list(all_names), resolved, strict=True):
                valid = await self._resolver.is_valid(resolved_setting)
                if mode == "Valid" and not valid:
                    all_names.pop(name)
                elif mode == "Invalid" and valid:
                    all_names.pop(name)

            return all_names
        else:
            raise ValueError(f"Unknown mode: {mode}")

    async def available_settings(
        self, dataset_name: str | None = None
    ) -> SettingsMenuType:
        """
        Get available settings menu for this registry.

        Parameters
        ----------
        dataset_name : str | None, default=None
            The name of the dataset to use when retrieving the settings menu.
            If not provided, the settings menu will be retrieved for the
            default dataset.

        Returns
        -------
        SettingsMenuType
            A description of valid settings for this registry.
        """
        if not callable(self._settings_menu):
            return self._settings_menu
        return await self._settings_menu(dataset_name)

    async def get_raw(self, name_or_id: list[str | int]) -> list[RawSettings]:
        """
        Get raw settings by names or IDs.

        Parameters
        ----------
        name_or_id : list[str | int]
            The list of names or identifiers to retrieve.

        Returns
        -------
        list[RawSettings]
            A list of raw settings corresponding to the input names or IDs.
        """
        references: list[tuple[ModelType, str | int]] = [
            (self._model_type.__name__, e) for e in name_or_id
        ]
        if len(references) == 0:
            return []
        return await self._resolver.resolve_references(references)

    async def get(self, name: str | int) -> SettingsType:
        """
        Get settings by name or ID.

        Parameters
        ----------
        name : str | int
            The name or identifier of the settings to retrieve.

        Returns
        -------
        SettingsType
            The retrieved settings.

        Raises
        ------
        KeyError
            If the settings could not be found.
        InvalidSettingsError
            If the settings exist but are invalid.
        """
        raw_settings = (
            await self._resolver.resolve_references([(self._model_type.__name__, name)])
        )[0]
        if not raw_settings.exists:
            raise KeyError(f"Could not find settings for input: {name}")
        if not await self._resolver.is_valid(raw_settings):
            raise InvalidSettingsError(raw_settings.raw_json)
        model = self._model_type.model_validate(raw_settings.raw_json)
        return model

    async def get_metadata(self, name: str | int) -> SettingsMetaData:
        """
        Get metadata for settings by name or ID.

        Parameters
        ----------
        name : str | int
            The name or identifier of the settings to retrieve metadata for.

        Returns
        -------
        SettingsMetaData
            The metadata for the specified settings.

        Raises
        ------
        KeyError
            If the settings could not be found.
        """
        try:
            if isinstance(name, int):
                return self._metadata[name]
            return self._metadata[(await self.names())[name]]
        except KeyError as e:
            raise KeyError(f"Could not find settings for input: {name}") from e

    async def _do_save(self, name: str, settings: SettingsType) -> int:
        if name in self._name_id_map:
            raise ValueError(f"Settings with name {name!r} already exists.")
        self._settings[self._next_id] = settings
        self._metadata[self._next_id] = SettingsMetaData(
            created_on=dt.datetime.now(tz=dt.timezone.utc),
            last_updated=dt.datetime.now(tz=dt.timezone.utc),
        )
        self._id_name_map[self._next_id] = name
        self._name_id_map[name] = self._next_id
        self._next_id += 1
        return self._next_id - 1

    async def _do_update(self, name: str | int, settings: SettingsType) -> RawSettings:
        try:
            previous = (await self.get_raw([name]))[0]

            if isinstance(name, int):
                self._settings[name] = settings
                self._metadata[name] = self._metadata[name].model_copy(
                    update={"last_updated": dt.datetime.now(tz=dt.timezone.utc)}
                )
                return previous
            idx = (await self.names())[name]
            self._settings[idx] = settings
            self._metadata[idx] = self._metadata[idx].model_copy(
                update={"last_updated": dt.datetime.now(tz=dt.timezone.utc)}
            )
            return previous
        except KeyError as e:
            raise KeyError(f"Could not find settings for input: {name}") from e

    async def delete(self, name: str | int) -> RawSettings:
        """
        Delete settings by name or ID.

        Parameters
        ----------
        name : str | int
            The name or identifier of the settings to delete.

        Returns
        -------
        RawSettings
            The deleted raw settings.

        Raises
        ------
        KeyError
            If the settings could not be found.
        """
        try:
            raw_settings = (await self.get_raw([name]))[0]
            if not raw_settings.exists:
                raise KeyError()

            raw_settings = raw_settings.model_copy(update={"exists": False})

            if isinstance(name, int):
                actual_name = self._id_name_map.pop(name)
                self._name_id_map.pop(actual_name)
                self._metadata.pop(name)
                self._settings.pop(name)
                return raw_settings
            idx = (await self.names())[name]
            self._id_name_map.pop(idx)
            self._name_id_map.pop(name)
            self._metadata.pop(idx)
            self._settings.pop(idx)
            return raw_settings
        except KeyError as e:
            raise KeyError(f"Could not find settings for input: {name}") from e


ApiType = TypeVar("ApiType")


class RegistryBasedApi(abc.ABC, Generic[SettingsType, SettingsMenuType, ApiType]):
    """Abstract base class for APIs based on registries."""

    @property
    @abc.abstractmethod
    def settings(self) -> SettingsRegistry[SettingsType, SettingsMenuType]:
        """Get the settings registry.

        Returns
        -------
        SettingsRegistry[SettingsType, SettingsMenuType]
            The settings registry instance.
        """
        ...

    @abc.abstractmethod
    def load(
        self, ref_or_settings: str | int | SettingsType, *args: Any, **kwargs: Any
    ) -> ApiType:
        """Load an API instance from settings or reference.

        Parameters
        ----------
        ref_or_settings : str | int | SettingsType
            Reference identifier, numeric ID, or settings object to load from.
        *args : Any
            Additional positional arguments passed to the loader.
        **kwargs : Any
            Additional keyword arguments passed to the loader.

        Returns
        -------
        ApiType
            The loaded API instance.
        """
        ...


@docstrings_from_sync
class AsyncRegistryBasedApi(abc.ABC, Generic[SettingsType, SettingsMenuType, ApiType]):

    @property
    @abc.abstractmethod
    def settings(  # noqa: D102
        self,
    ) -> AsyncSettingsRegistry[SettingsType, SettingsMenuType]: ...

    @abc.abstractmethod
    async def load(  # noqa: D102
        self, ref_or_settings: str | int | SettingsType, *args: Any, **kwargs: Any
    ) -> ApiType: ...
