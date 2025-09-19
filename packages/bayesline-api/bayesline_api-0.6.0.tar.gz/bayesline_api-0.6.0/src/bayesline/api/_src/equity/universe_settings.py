import json
import os
from collections.abc import Mapping
from typing import Annotated, Any, Literal, Self

import polars as pl
from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    NonNegativeFloat,
    field_validator,
    model_validator,
)

from bayesline.api._src.equity import settings as settings_tools
from bayesline.api._src.equity.calendar_settings import (
    CalendarSettings,
    CalendarSettingsMenu,
    require_sorted_unique,
)
from bayesline.api._src.registry import Settings, SettingsMenu
from bayesline.api._src.types import IdType

Hierarchy = settings_tools.Hierarchy


class CategoricalFilterSettings(BaseModel, frozen=True, extra="forbid"):
    """Specify include and exclude filters for categorical codes.

    Examples of categorical codes are industries or countries. Assets are included if
    they are part of at least one include and not part of any exclude.

    By default all codes for the given hierarchy are included.
    """

    hierarchy: str = Field(
        min_length=1,
        description="The categorical hierarchy to use.",
        examples=["trbc"],
    )

    include: list[str] | Literal["All"] = Field(
        default="All",
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the highest "
            "level is used. If 'All', all codes are included."
        ),
        examples=[["3571"], "All", ["Materials", "1010"], ["Europe", "CAN"]],
    )

    exclude: list[str] = Field(
        default_factory=list,
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the lowest "
            "level is used."
        ),
        examples=[["3571"], ["Materials", "1010"], ["JPN"]],
    )


class MCapFilterSettings(BaseModel, frozen=True, extra="forbid"):
    """Specify the lower and upper bound for the market cap filter.

    By default the bounds are infinite.
    """

    lower: NonNegativeFloat = Field(
        default=0.0,
        ge=0.0,
        description="Lower bound of the cap filter in USD.",
        examples=[1e10],
    )

    upper: NonNegativeFloat = Field(
        default=1e20,
        gt=0.0,
        description="Upper bound of the cap filter in USD.",
        examples=[1e12],
    )

    @model_validator(mode="after")
    def check_upper_gt_lower(self) -> Self:
        """Validate that the upper bound is greater than the lower bound.

        Returns
        -------
        Self
            The validated instance.

        Raises
        ------
        ValueError
            If the upper bound is not greater than the lower bound.
        """
        if (lower := self.lower) >= (upper := self.upper):
            raise ValueError(
                f"upper bound {upper} must be greater than lower bound {lower}",
            )
        else:
            return self


class UniverseSettings(Settings):
    """Define an asset universe as a set of regional, industry and market cap filters."""

    dataset: str = Field(
        description=(
            "The name of the underlying dataset to use. If none is given then the "
            "configured default dataset is used."
        ),
        examples=["Bayesline-Global"],
    )

    id_type: IdType = Field(
        default="bayesid",
        description="The default id type to use for the universe.",
        examples=["cusip9", "bayesid"],
    )

    calendar: CalendarSettings = Field(
        default_factory=CalendarSettings,
        description="The calendar settings to use for the universe.",
    )

    categorical_filters: list[CategoricalFilterSettings] = Field(
        default_factory=list,
        description="""
        Filters that determine which categorical codes to include and exclude in the universe.
        """,
    )

    mcap_filter: MCapFilterSettings = Field(
        default_factory=MCapFilterSettings,
        description="""
        Filters that determine which market caps to include and exclude in the universe.
        """,
    )

    @field_validator("categorical_filters")
    @classmethod
    def check_unique_filters(
        cls: type["UniverseSettings"], v: list[CategoricalFilterSettings]
    ) -> list[CategoricalFilterSettings]:
        """Validate that categorical filters reference unique hierarchies.

        Parameters
        ----------
        v : list[CategoricalFilterSettings]
            The list of categorical filter settings to validate.

        Returns
        -------
        list[CategoricalFilterSettings]
            The validated list of filter settings.

        Raises
        ------
        ValueError
            If any hierarchy is referenced multiple times.
        """
        factor_groups = [filter_settings.hierarchy for filter_settings in v]
        if len(factor_groups) != len(set(factor_groups)):
            raise ValueError("categorical_filters must reference unique hierarchies")
        return v

    @model_validator(mode="before")
    @classmethod
    def propagate_dataset(cls: type["UniverseSettings"], data: Any) -> Any:
        """Propagate the dataset to the calendar.

        Parameters
        ----------
        data : Any
            The input data for the model validation.

        Returns
        -------
        Any
            The modified data with dataset propagated to calendar.
        """
        if isinstance(data, dict) and "dataset" in data:
            if "calendar" not in data:
                data["calendar"] = {}
            if isinstance(data["calendar"], dict):
                if data["calendar"].get("dataset") is None:
                    data["calendar"]["dataset"] = data["dataset"]
        return data


class UniverseSettingsMenu(SettingsMenu, frozen=True, extra="forbid"):
    """Contain the available settings that can be used for the universe settings."""

    id_types: list[IdType] = Field(
        description="""
        A list of all the id types that are supported for the universe.
        """,
    )

    exchanges: Annotated[list[str], AfterValidator(require_sorted_unique)] = Field(
        description="""
        A list of mic codes of all exchanges. Must be sorted and unique.
        """,
    )

    categorical_hierarchies: Mapping[str, Hierarchy] = Field(
        description="""
        A dictionary where the key is the name of the categorical hierarchy (e.g. 'trbc')
        and the value is a N-level nested dictionary structure of the categorical hierarchy
        codes.
        """,
    )

    categorical_hierarchies_labels: Mapping[str, Mapping[str, str]] = Field(
        description="""
        A dictionary where the key is the name of the categorical hierarchy and
        the value is a mapping from unique categorical code to a human readable name.
        """,
    )

    def describe(self, settings: UniverseSettings | None = None) -> str:
        """Generate a human-readable description of the universe settings.

        Parameters
        ----------
        settings : UniverseSettings | None, default=None
            The universe settings to describe. If None, describes the available options.

        Returns
        -------
        str
            A formatted description of the universe settings or available options.
        """
        hierarchies = self.categorical_hierarchies
        labels = self.categorical_hierarchies_labels

        if settings is not None:
            self.validate_settings(settings)
            description = [f"Default ID Type: {settings.id_type!r}"]

            for filter_settings in settings.categorical_filters:
                hierarchy_name = filter_settings.hierarchy
                effective_hierarchy = settings_tools.effective_hierarchy(
                    hierarchies[hierarchy_name],
                    filter_settings.include,
                    filter_settings.exclude,
                    labels[hierarchy_name],
                )
                effective_hierarchy = settings_tools.codes_to_labels(
                    effective_hierarchy, labels[hierarchy_name]
                )
                description.extend(
                    [
                        f"Hierarchy ({hierarchy_name}):",
                        json.dumps(effective_hierarchy, indent=2),
                    ]
                )

            description.extend(
                [
                    "Market Cap:",
                    settings.mcap_filter.model_dump_json(indent=2),
                ]
            )
        else:
            hierarchies_str = json.dumps(
                {
                    k: settings_tools.codes_to_labels(hierarchies[k], labels[k])
                    for k in hierarchies
                },
                indent=2,
            )
            id_types = ", ".join(self.id_types)
            description = [
                f"ID Types: {id_types}",
                "Hierarchies:",
                hierarchies_str,
            ]

        return os.linesep.join(description)

    @field_validator("categorical_hierarchies")
    @classmethod
    def check_unique_hierarchy(
        cls: type["UniverseSettingsMenu"], v: Mapping[str, Hierarchy]
    ) -> Mapping[str, Hierarchy]:
        """Validate that categorical hierarchies have unique codes.

        Parameters
        ----------
        v : Mapping[str, Hierarchy]
            The mapping of hierarchy names to hierarchies.

        Returns
        -------
        Mapping[str, Hierarchy]
            The validated mapping.

        Raises
        ------
        ValueError
            If any hierarchy contains duplicate codes.
        """
        return settings_tools.check_unique_hierarchy(v)

    @field_validator("categorical_hierarchies")
    @classmethod
    def check_no_empty_branches(
        cls,
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        """Validate that categorical hierarchies have no empty branches.

        Parameters
        ----------
        v : Mapping[str, Mapping[str, Hierarchy]]
            The mapping of hierarchy names to hierarchies.

        Returns
        -------
        Mapping[str, Mapping[str, Hierarchy]]
            The validated mapping.

        Raises
        ------
        ValueError
            If any hierarchy is empty or contains empty branches.
        """
        for hierarchy_name, hierarchy in v.items():
            if not hierarchy:  # different error message at root level
                raise ValueError(f"Hierarchy '{hierarchy_name}' cannot be empty")
            settings_tools.assert_no_empty_branches(hierarchy, hierarchy_name)
        return v

    @model_validator(mode="after")
    def check_all_codes_have_labels(self) -> Self:
        """Validate that all categorical codes have corresponding labels.

        Returns
        -------
        Self
            The validated instance.

        Raises
        ------
        ValueError
            If any categorical code is missing a label.
        """
        if errors := settings_tools.check_all_codes_have_labels(
            self.categorical_hierarchies,
            self.categorical_hierarchies_labels,
        ):
            raise ValueError(os.linesep.join(errors))
        else:
            return self

    def effective_categories(
        self,
        settings: CategoricalFilterSettings,
        labels: bool = False,
    ) -> list[str]:
        """Get the effective leaf level categorical codes after categorical filtering.

        Parameters
        ----------
        settings : CategoricalFilterSettings
            The filter settings to get the effective categorical codes for.
        labels : bool, default=False
            Whether to return the labels or the codes.

        Returns
        -------
        list[str]
            The effective leaf level categorical codes for the given settings after the
            filters were applied.
        """
        self.validate_categorical_filter_settings(settings)
        effective_codes = settings_tools.effective_leaves(
            self.categorical_hierarchies[settings.hierarchy],
            settings.include,
            settings.exclude,
            self.categorical_hierarchies_labels[settings.hierarchy],
        )
        if labels:
            return [
                self.categorical_hierarchies_labels[settings.hierarchy][code]
                for code in effective_codes
            ]
        else:
            return effective_codes

    def validate_settings(self, settings: UniverseSettings) -> None:
        """Validate the given universe settings against the available settings.

        Will raise a `ValueError` if settings are invalid.

        Parameters
        ----------
        settings : UniverseSettings
            The universe settings to validate against.

        Raises
        ------
        ValueError
            If the id type does not exist or if calendar or categorical filter
            settings are invalid.
        """
        if settings.id_type not in self.id_types:
            raise ValueError(
                f"""
                Id type {settings.id_type} does not exist.
                Only {', '.join(self.id_types)} exist.
                """,
            )
        self.validate_calendar(settings.calendar)
        for filter_settings in settings.categorical_filters:
            self.validate_categorical_filter_settings(filter_settings)

    def validate_calendar(self, settings: CalendarSettings) -> None:
        """Validate the given calendar settings against the available settings.

        Will raise a `ValueError` if settings are invalid.

        Parameters
        ----------
        settings : CalendarSettings
            The calendar settings to validate against.

        Raises
        ------
        ValueError
            If settings is None or if exchange validation fails.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        CalendarSettingsMenu._validate_exchanges(self.exchanges, settings)

    def validate_categorical_filter_settings(
        self, settings: CategoricalFilterSettings
    ) -> None:
        """Validate the given categorical filter settings against the available settings.

        Will raise a `ValueError` if settings are invalid.

        Parameters
        ----------
        settings : CategoricalFilterSettings
            The settings to validate against.

        Raises
        ------
        ValueError
            If settings is None or if hierarchy validation fails.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        settings_tools.validate_hierarchy_schema(
            self.categorical_hierarchies, settings.hierarchy
        )
        settings_tools.validate_hierarchy_filters(
            self.categorical_hierarchies[settings.hierarchy],
            settings.include,
            settings.exclude,
            self.categorical_hierarchies_labels[settings.hierarchy],
        )

    def hierarchy_df(self, hierarchy: str) -> pl.DataFrame:
        """Return a dataframe of the given categorical hierarchy.

        Parameters
        ----------
        hierarchy : str
            The name of the categorical hierarchy to return.

        Returns
        -------
        pl.DataFrame
            The wide DataFrame representation of the hierarchy. The columns are:
            - level_1: The code of the root level.
            - level_1_label: The label of the root level.
            - level_2: The code of the second level.
            - level_2_label: The label of the second level.
            - ...
            - level_n: The code of the n-th level.
            - level_n_label: The label of the n-th level.
        """
        return settings_tools.hierarchy_df_to_wide(
            self.categorical_hierarchies[hierarchy],
            self.categorical_hierarchies_labels[hierarchy],
        )
