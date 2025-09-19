import json
import os
from collections.abc import Mapping
from typing import Annotated, Any, Literal, Self

import polars as pl
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    NonNegativeFloat,
    field_validator,
    model_validator,
)

from bayesline.api._src.equity import settings as settings_tools
from bayesline.api._src.equity.universe_settings import UniverseSettings
from bayesline.api._src.registry import Settings, SettingsMenu

Hierarchy = settings_tools.Hierarchy


def _ensure_list(value: Any) -> Any:
    if isinstance(value, list | tuple):
        return value
    return [value]


class HierarchyDescription(BaseModel, frozen=True, extra="forbid"):
    """Base class for hierarchy descriptions."""

    hierarchy_type: Literal["level", "groups"]
    name: str = Field(
        min_length=1,
        description="""
        The name of the hierarchy to use, e.g. 'trbc' or 'continent'.
        If it is not given then the default hierarchy will be used.
        """,
        examples=["trbc", "continent"],
    )


class HierarchyLevel(HierarchyDescription):
    """The hierarchy decscription for a level in the hierarchy.

    E.g. for industries specifying level `1` would
    create top level sector factors.
    """

    hierarchy_type: Literal["level"] = "level"
    level: int = Field(
        description="""The level of the hierarchy to use, e.g. 1
        to use all level 1 names (i.e. sectors for industries or
        continents for regions) or 2 to use all level 2
        names (i.e. sub-sectors for industries and
        countries for regions).
        """,
        default=1,
        examples=[1, 2],
        ge=1,
    )


class HierarchyGroups(HierarchyDescription):
    """The hierarchy decscription for a custom nested grouping of the hierarchy.

    The top level groupings will turn into factors, whereas any nested
    groupings will be retained for other uses (e.g. risk decomposition).
    """

    hierarchy_type: Literal["groups"] = "groups"
    groupings: Mapping[str, Hierarchy] = Field(  # at least two levels deep
        description="""
        A nested structure of groupings where the keys are the group names
        and the leaf level is a list of hierarchy codes or labels (at any level)
        to include for this group.
        """,
    )

    @field_validator("groupings")
    @classmethod
    def check_valid_groupings(
        cls, v: Mapping[str, Hierarchy]
    ) -> Mapping[str, Hierarchy]:
        settings_tools.check_unique_hierarchy(v)
        settings_tools.assert_no_empty_branches(v)
        leaves = settings_tools.flatten(v, only_leaves=True)
        if len(leaves) != len(set(leaves)):
            raise ValueError(
                "Groupings must be unique in the sense that no code or label occurs "
                "under any group name."
            )
        return v


def _hierarchy_name_to_hierarchy_level(
    v: HierarchyLevel | HierarchyGroups | str,
) -> HierarchyLevel | HierarchyGroups:
    # accept strings and turn them into a level-1 HierarchyLevel
    if isinstance(v, str):
        return HierarchyLevel(name=v, level=1)
    return v


HierarchyType = Annotated[
    HierarchyLevel | HierarchyGroups,
    Field(discriminator="hierarchy_type"),
    BeforeValidator(_hierarchy_name_to_hierarchy_level),
]


class ContinuousExposureGroupSettings(BaseModel, frozen=True, extra="forbid"):
    """The settings for a continuous exposure group.

    Continuous exposures are exposures that are measured on a continuous scale,
    e.g. market, size, momentum, etc., and are typically available for most assets.
    """

    exposure_type: Literal["continuous"] = "continuous"
    hierarchy: Annotated[
        HierarchyType,
        Field(
            description=(
                "The hierarchy to use for the continuous exposures. This is either a"
                "HierarchyLevel or HierarchyGroups object. If a string is passed, the "
                "value is converted to a HierarchyLevel of that hierarchy with level=1."
            ),
            examples=[
                "market",
                HierarchyLevel(name="style", level=2),
                HierarchyGroups(
                    name="style",
                    groupings={
                        "momentum": ["mom6"],
                        "size": ["size"],
                    },
                ),
            ],
        ),
    ]
    factor_group: str = Field(
        "",  # temporary value that does not pass validation
        description=(
            "By default, the name of the factor group will be the name of the hierarchy. "
            "But we can override this by specifying an alias here."
        ),
        examples=["style", "some_style_group"],
    )
    include: Literal["All"] | list[str] = Field(
        default="All",
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the highest "
            "level is used. If 'All', all codes are included."
        ),
        examples=[["momentum"], "All", ["Size", "value"]],
    )
    exclude: list[str] = Field(
        default_factory=list,
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the lowest "
            "level is used."
        ),
        examples=[["momentum"], ["Size", "value"]],
    )
    standardize_method: Literal["none", "equal_weighted"] = Field(
        "none",
        description=(
            "The method to use for standardizing the exposures. If 'none', no "
            "standardization is applied. If 'equal_weighted', then the exposures are "
            "standardized with the mean and standard deviation of the estimation "
            "universe."
        ),
        examples=["none", "equal_weighted"],
    )
    known_factor_map: Mapping[str, str] = Field(
        default_factory=dict,
        description=(
            "A mapping from factor names (labels) to known series. These factors will "
            "have fixed returns derived from the series."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def set_factor_group(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "factor_group" not in data or data["factor_group"] is None:
                if isinstance(data["hierarchy"], HierarchyLevel | HierarchyGroups):
                    data["factor_group"] = data["hierarchy"].name
                elif isinstance(data["hierarchy"], str):
                    data["factor_group"] = data["hierarchy"]
                else:
                    raise ValueError(
                        f"Invalid hierarchy type: {type(data['hierarchy'])}"
                    )
        return data

    @field_validator("factor_group")
    @classmethod
    def check_valid_factor_group(cls, v: str) -> str:
        if v == "":
            raise ValueError("factor_group cannot be empty")
        return v


class CategoricalExposureGroupSettings(BaseModel, frozen=True, extra="forbid"):
    """The settings for a categorical exposure group.

    Categorical exposures are exposures to a categorical variable, e.g. industry,
    country, etc. For example, an asset exposure may be to a single industry factor,
    and we say the exposure is to the industry category factor "Materials". The exposure
    itself may be continuous (e.g. not 0.0 or 1.0), and an asset may be exposed to
    multiple industry factors (but typically not all of them). The distinction with
    continuous exposures is primarily in the settings that are available.
    """

    exposure_type: Literal["categorical"] = "categorical"
    hierarchy: Annotated[
        HierarchyType,
        Field(
            description=(
                "The hierarchy to use for the categorical exposures. This is either a"
                "HierarchyLevel or HierarchyGroups object. If a string is passed, the "
                "value is converted to a HierarchyLevel of that hierarchy with level=1."
            ),
            examples=[
                "trbc",
                HierarchyLevel(name="trbc", level=2),
                HierarchyGroups(
                    name="style",
                    groupings={
                        "MyGroup1": ["Energy"],
                        "MyGroup2": ["Materials", "Chemicals"],
                    },
                ),
            ],
        ),
    ]
    factor_group: str = Field(
        "",
        description=(
            "By default, the name of the factor group will be the name of the hierarchy. "
            "But we can override this by specifying an alias here."
        ),
        examples=["industry", "some_country_group"],
    )
    include: Literal["All"] | list[str] = Field(
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
    thin_factor_correction_regulatization_strength: NonNegativeFloat = 0.0
    regulatization_strength: NonNegativeFloat | dict[str, NonNegativeFloat] = 0.0
    zero_sum_constraint: Literal["none", "equal_weights", "mcap_weighted"] = Field(
        description=(
            "Whether to apply a zero-sum constraint to the exposures. If the "
            "category exposures are exhaustive and sum to one, then implicitly a dummy "
            "variable trap is present. This can be avoided by creating a constraint on "
            "the factor returns. This means the interpretation of the categorical "
            "factor returns is 'in excess of' the market. If 'none', no constraint is "
            "applied (for example if we do not have a market factor). If "
            "'equal_weights' or 'mcap_weighted', then the categorical factor returns "
            "are constrained to sum to zero, either market-cap weighted or not."
        ),
        examples=["none", "equal_weights", "mcap_weighted"],
    )

    @model_validator(mode="before")
    @classmethod
    def set_factor_group(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "factor_group" not in data or data["factor_group"] is None:
                if isinstance(data["hierarchy"], HierarchyLevel | HierarchyGroups):
                    data["factor_group"] = data["hierarchy"].name
                elif isinstance(data["hierarchy"], str):
                    data["factor_group"] = data["hierarchy"]
                else:
                    raise ValueError(
                        f"Invalid hierarchy type: {type(data['hierarchy'])}"
                    )
        return data

    @field_validator("factor_group")
    @classmethod
    def check_valid_factor_group(cls, v: str) -> str:
        if v == "":
            raise ValueError("factor_group cannot be empty")
        return v


ExposureGroupSettings = Annotated[
    ContinuousExposureGroupSettings | CategoricalExposureGroupSettings,
    Field(discriminator="exposure_type"),
]


def _normalize_hierarchy(
    hierarchy: HierarchyLevel | HierarchyGroups,
    reference_hierarchy: Hierarchy,
    reference_labels: Mapping[str, str],
) -> HierarchyGroups:
    groupings: dict[str, list[str]] = {}
    if isinstance(hierarchy, HierarchyLevel):
        keys = settings_tools.flatten(
            settings_tools.trim_to_depth(reference_hierarchy, hierarchy.level),
            only_leaves=True,
        )
        for k in keys:
            sub_hierarchy = settings_tools.find_in_hierarchy(reference_hierarchy, k)
            if sub_hierarchy is not None:
                k = reference_labels.get(k, k)  # convert top level to label if possible
                groupings[k] = settings_tools.flatten(
                    sub_hierarchy,
                    only_leaves=True,
                )
    else:  # HierarchyGroups
        for k, v in hierarchy.groupings.items():
            groupings[k] = []
            # v is a Hierarchy, first map the codes to labels (with ~ prefix)
            v = settings_tools.labels_to_codes(v, reference_labels, prefix="~")
            # then process the excludes
            v = settings_tools.process_excludes(v, reference_hierarchy)
            # then flatten the hierarchy
            for code in v:
                sub_hierarchy = settings_tools.find_in_hierarchy(
                    reference_hierarchy, code
                )
                if sub_hierarchy is not None:
                    groupings[k].extend(
                        settings_tools.flatten(sub_hierarchy, only_leaves=True)
                    )
    return HierarchyGroups(
        name=hierarchy.name,
        groupings=groupings,
    )


class ExposureSettings(Settings):
    """Defines exposures as hierarchy of selected styles and substyles."""

    exposures: Annotated[
        list[ExposureGroupSettings],
        BeforeValidator(_ensure_list),
        Field(
            description="The exposures to build the factor risk model on.",
        ),
    ] = []


class ExposureSettingsMenu(SettingsMenu[ExposureSettings], frozen=True, extra="forbid"):
    """Contains the available settings that can be used to define exposures."""

    continuous_hierarchies: Mapping[str, Hierarchy] = Field(
        description="""
        A dictionary where the key is the name of the continuous hierarchy (e.g. 'style')
        and the value is a N-level nested dictionary structure of the continuous hierarchy
        codes.
        """,
    )

    continuous_hierarchies_labels: Mapping[str, Mapping[str, str]] = Field(
        description="""
        A dictionary where the key is the name of the continuous hierarchy and
        the value is a mapping from unique continuous code to a human readable name.
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

    @property
    def hierarchies(self) -> Mapping[str, Hierarchy]:
        """The combined hierarchies from the continuous and categorical hierarchies.

        Returns
        -------
        Mapping[str, Hierarchy]
            A dictionary where the key is the name of the hierarchy and
            the value is the hierarchy.
        """
        return {**self.continuous_hierarchies, **self.categorical_hierarchies}

    @property
    def hierarchies_labels(self) -> Mapping[str, Mapping[str, str]]:
        """The combined hierarchies labels from the continuous and categorical hierarchies.

        Returns
        -------
        Mapping[str, Mapping[str, str]]
            A dictionary where the key is the name of the hierarchy and
            the value is a mapping from unique code to a human readable name.
        """
        return {
            **self.continuous_hierarchies_labels,
            **self.categorical_hierarchies_labels,
        }

    def normalize(
        self,
        universe_settings: UniverseSettings | None,
        exposure_settings: ExposureSettings,
    ) -> ExposureSettings:
        """Normalize the given exposure settings.

        Normalize the given exposure settings by converting all exposure hierarchies
        to a HierarchyGroups object, and then filtering the hierarchy groupings based
        on the include and exclude statements in the exposure settings, and possibly
        the universe filters.

        Parameters
        ----------
        universe_settings: UniverseSettings | None
                the universe settings to use for normalization. If None, then no
                normalization is performed in relation to the filters in the universe.
        exposure_settings: ExposureSettings
                the exposure settings to normalize.

        Returns
        -------
        ExposureSettings
            A new exposure settings object with all exposure hierarchies converted to
            HierarchyGroups objects, and the hierarchy groupings filtered based on the
            include and exclude statements in the exposure settings, and possibly the
            universe filters. This normalized object is also validated.
        """
        exposure_settings = exposure_settings.model_copy(deep=True)  # no modification

        if universe_settings:
            universe_filter_dict = {
                filter_settings.hierarchy: filter_settings  # hierarchy is unique
                for filter_settings in universe_settings.categorical_filters
            }

        for group_settings in exposure_settings.exposures:
            # normalize the hierarchy to Mapping[str, list[str]] with all leaf codes
            name = group_settings.hierarchy.name
            hierarchy_groups = _normalize_hierarchy(
                group_settings.hierarchy,
                self.hierarchies[name],
                self.hierarchies_labels[name],
            )
            # filter based on include and exclude
            new_groupings = settings_tools.effective_hierarchy(
                hierarchy_groups.groupings,
                group_settings.include,
                group_settings.exclude,
                self.hierarchies_labels[name],
            )
            object.__setattr__(hierarchy_groups, "groupings", new_groupings)
            if universe_settings:
                # filter the hierarchy groupings down if the universe has filters
                if name in universe_filter_dict:  # filter the hierarchy groupings down
                    filter_settings = universe_filter_dict[name]
                    effective_leaves = settings_tools.effective_leaves(
                        self.hierarchies[name],
                        filter_settings.include,
                        filter_settings.exclude,
                        self.hierarchies_labels[name],
                    )
                    new_groupings = {
                        k: filtered_leaves
                        for k, v in hierarchy_groups.groupings.items()
                        if (filtered_leaves := [w for w in v if w in effective_leaves])
                    }
                    object.__setattr__(hierarchy_groups, "groupings", new_groupings)
            object.__setattr__(group_settings, "hierarchy", hierarchy_groups)  # frozen
            # normalized group settings should not have includes / excludes
            object.__setattr__(group_settings, "include", "All")
            object.__setattr__(group_settings, "exclude", [])

        # we may have produced an invalid settings object with the __setattr__ calls
        # so we need to validate again (validate_settings does pydantic validation)
        self.validate_settings(exposure_settings)

        return exposure_settings

    def effective_exposure_group_factors(
        self, group_settings: ExposureGroupSettings
    ) -> list[str]:
        """Get the effective factors for the given exposure group settings.

        Effective factors are the factors that are included and not excluded in the
        exposure group settings.

        Parameters
        ----------
        group_settings: ExposureGroupSettings
            The exposure group settings to get the effective factors for.

        Returns
        -------
        list[str]
            The effective factors for the given exposure group settings.
        """
        self.validate_exposure_group_settings(group_settings)
        hierarchy_name = group_settings.hierarchy.name
        hierarchy_groups = _normalize_hierarchy(
            group_settings.hierarchy,
            self.hierarchies[hierarchy_name],
            self.hierarchies_labels[hierarchy_name],
        )
        # filter based on include and exclude
        effective_groupings = settings_tools.effective_hierarchy(
            hierarchy_groups.groupings,
            group_settings.include,
            group_settings.exclude,
            self.hierarchies_labels[hierarchy_name],
        )
        # just return the keys of effective_groupings
        return list(effective_groupings)

    def describe(self, settings: ExposureSettings | None = None) -> str:
        """Describe the given exposure settings.

        Parameters
        ----------
        settings: ExposureSettings | None, default=None
            The exposure settings to describe. If None, the menu itself is described.

        Returns
        -------
        str
            The description of the given exposure settings.
        """
        # only describe continuous hierarchies for now
        hierarchies = self.continuous_hierarchies
        labels = self.continuous_hierarchies_labels

        if settings is not None:
            self.validate_settings(settings)
            settings = self.normalize(None, settings)
            description = []
            for group_settings in settings.exposures:
                hierarchy_name = group_settings.hierarchy.name
                hierarchy = settings_tools.codes_to_labels(
                    hierarchies[hierarchy_name], labels[hierarchy_name]
                )
                description.extend(
                    [
                        f"Hierarchy ({hierarchy_name}):",
                        json.dumps(hierarchy, indent=2),
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
            description = [
                "Hierarchies:",
                hierarchies_str,
            ]

        return os.linesep.join(description)

    @field_validator("continuous_hierarchies", "categorical_hierarchies")
    @classmethod
    def check_unique_hierarchy(
        cls,
        v: Mapping[str, Hierarchy],
    ) -> Mapping[str, Hierarchy]:
        return settings_tools.check_unique_hierarchy(v)

    @field_validator("continuous_hierarchies", "categorical_hierarchies")
    @classmethod
    def check_no_empty_branches(
        cls,
        v: Mapping[str, Hierarchy],
    ) -> Mapping[str, Hierarchy]:
        for hierarchy_name, hierarchy in v.items():
            if not hierarchy:  # different error message at root level
                raise ValueError(f"Hierarchy '{hierarchy_name}' cannot be empty")
            settings_tools.assert_no_empty_branches(hierarchy, hierarchy_name)
        return v

    @model_validator(mode="after")
    def check_all_codes_have_labels(self) -> Self:
        if errors := settings_tools.check_all_codes_have_labels(
            self.hierarchies, self.hierarchies_labels
        ):
            raise ValueError(os.linesep.join(errors))
        else:
            return self

    def validate_settings(self, settings: ExposureSettings) -> None:
        """Validate the given exposure settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: ExposureSettings
                  the exposure settings to validate against.
        """
        settings.model_validate(settings.model_dump())  # basic pydantic validation

        factor_dict: dict[str, list[str]] = {}  # to collect factors per factor_group
        for group_settings in settings.exposures:
            self.validate_exposure_group_settings(group_settings)
            factor_dict.setdefault(group_settings.factor_group, []).extend(
                self.effective_exposure_group_factors(group_settings)
            )

        # check that output factor_group-factor combinations are unique
        settings_tools.check_unique_hierarchy(factor_dict)

    def validate_exposure_group_settings(  # noqa: C901
        self, settings: ExposureGroupSettings
    ) -> None:
        """Validate the given exposure settings group against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: ExposureGroupSettings
                  the exposure settings group to validate against.

        Raises
        ------
        ValueError
            If settings are invalid.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        # validate that the hierarchies exist
        if settings.exposure_type == "categorical":
            settings_tools.validate_hierarchy_schema(
                self.categorical_hierarchies, settings.hierarchy.name
            )
        if settings.exposure_type == "continuous":
            settings_tools.validate_hierarchy_schema(
                self.continuous_hierarchies, settings.hierarchy.name
            )

        # common validation
        settings_tools.validate_hierarchy_filters(
            self.hierarchies[settings.hierarchy.name],
            settings.include,
            settings.exclude,
            self.hierarchies_labels[settings.hierarchy.name],
        )

        # validation dependent on the hierarchy type
        hierarchy = settings.hierarchy
        if isinstance(hierarchy, HierarchyGroups):
            leaves_without_prefix = [  # strip the ~ prefix from the leaves
                g[1:] if g.startswith("~") else g
                for g in settings_tools.flatten(hierarchy.groupings, only_leaves=True)
            ]
            if non_leaves_with_prefix := [
                g
                for g in (
                    set(settings_tools.flatten(hierarchy.groupings))
                    - set(settings_tools.flatten(hierarchy.groupings, only_leaves=True))
                )
                if g.startswith("~")
            ]:
                raise ValueError(
                    "Only leaves can have the exlude prefix ~. The following "
                    f"non-leaves have a ~ prefix: {', '.join(non_leaves_with_prefix)}."
                )
            effective_codes = settings_tools.labels_to_codes(  # prefix not resolved
                leaves_without_prefix, self.hierarchies_labels[hierarchy.name]
            )
            available_codes = settings_tools.flatten(
                self.hierarchies[hierarchy.name], only_leaves=False
            )
            if missing := set(effective_codes) - set(available_codes):
                raise ValueError(
                    "The following codes are in the hierarchy but not in the hierarchy "
                    f"groups: {', '.join(missing)}"
                )
        if isinstance(hierarchy, HierarchyLevel):
            max_level = settings_tools.get_depth(self.hierarchies[hierarchy.name])
            if hierarchy.level > max_level:
                raise ValueError(
                    f"Illegal level {hierarchy.level}, maximum level is {max_level}"
                )

        # if continuous, check that the known_factor_map is valid
        if settings.exposure_type == "continuous":
            if settings.known_factor_map:
                normalized_hierarchy = _normalize_hierarchy(
                    settings.hierarchy,
                    self.continuous_hierarchies[hierarchy.name],
                    self.continuous_hierarchies_labels[hierarchy.name],
                )
                new_groupings = settings_tools.effective_hierarchy(
                    normalized_hierarchy.groupings,
                    settings.include,
                    settings.exclude,
                    self.continuous_hierarchies_labels[hierarchy.name],
                )
                object.__setattr__(normalized_hierarchy, "groupings", new_groupings)
                normalized_hierarchy.model_validate(normalized_hierarchy.model_dump())
                known_factors = settings_tools.codes_to_labels(
                    list(settings.known_factor_map),
                    self.continuous_hierarchies_labels[hierarchy.name],
                )
                if missing := set(known_factors) - set(normalized_hierarchy.groupings):
                    raise ValueError(
                        f"Factors {', '.join(missing)} are in known_factor_map but not "
                        "found in the hierarchy: "
                        f"{', '.join(normalized_hierarchy.groupings.keys())}"
                    )

    def hierarchy_df(self, hierarchy: str) -> pl.DataFrame:
        """Return a dataframe of the given hierarchy.

        Parameters
        ----------
        hierarchy: str
            the name of the hierarchy to return.

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
            self.hierarchies[hierarchy], self.hierarchies_labels[hierarchy]
        )
