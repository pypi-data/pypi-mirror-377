from typing import Annotated, Literal

from pydantic import Field

from bayesline.api._src.registry import Settings, SettingsMenu, SettingsTypeMetaData


class PortfolioOrganizerSettings(Settings):
    """
    Specifies which portfolios to enable (from different sources).

    Different sources (e.g. uploaded portfolios) can provide the same portfolio
    identifiers. These settings allow to specify which portfolios to enable from
    which sources.
    """

    dataset: str | None = Field(
        default=None,
        description=(
            "The name of the underlying dataset to use for price data needed to "
            "forward fill portfolios, obtain corporate actions, etc."
            "If none is given then the configured default dataset is used."
        ),
        examples=["Bayesline-US"],
    )

    enabled_portfolios: str | dict[str, str] = Field(
        description=(
            "The enabled portfolios from different sources. "
            "The key is the portfolio ID, and the value is the source "
            "(name of the underlying portfolio service). "
            "Pass a str to reference an entire portfolio source (e.g. all portfolios "
            "from an upload)."
        ),
    )


class PortfolioOrganizerSettingsMenu(
    SettingsMenu[PortfolioOrganizerSettings], frozen=True, extra="forbid"
):
    """Menu for portfolio organizer settings.

    This class provides a menu interface for managing portfolio organizer settings
    and available portfolio sources.
    """

    sources: dict[str, list[str]] = Field(
        description=(
            "Mapping of sources to the available portfolio IDs for that source."
        )
    )

    def describe(self, settings: PortfolioOrganizerSettings | None = None) -> str:
        """Describe the available sources or settings.

        Parameters
        ----------
        settings : PortfolioOrganizerSettings | None, default=None
            The settings to describe, or None to describe available sources.

        Returns
        -------
        str
            A description of the available sources or settings.
        """
        if settings is None:
            return f"Sources: {self.sources}"
        else:
            enabled_portfolios = settings.enabled_portfolios
            return f"Enabled Portfolios: {enabled_portfolios}"

    def validate_settings(self, settings: PortfolioOrganizerSettings) -> None:
        """Validate the portfolio organizer settings.

        Parameters
        ----------
        settings : PortfolioOrganizerSettings
            The settings to validate.

        Raises
        ------
        ValueError
            If the source is unknown or portfolio ID is not found in the source.
        """
        messages = []

        if isinstance(settings.enabled_portfolios, str):
            if settings.enabled_portfolios not in self.sources:
                messages.append(
                    f"Invalid source: {settings.enabled_portfolios}. "
                    f"Available sources: {', '.join(self.sources.keys())}. "
                )
        else:
            for portfolio_id, source in settings.enabled_portfolios.items():
                if source not in self.sources:
                    messages.append(
                        f"Invalid source: {source}. "
                        f"Available sources: {', '.join(self.sources.keys())}. "
                    )
                elif portfolio_id not in self.sources[source]:
                    messages.append(
                        f"Invalid portfolio ID: {portfolio_id} for source {source}. "
                    )
        if messages:
            raise ValueError("".join(messages))


class PortfolioSettings(Settings):
    """Specifies different options of obtaining portfolios."""

    portfolio_schema: Annotated[
        str | int | PortfolioOrganizerSettings,
        Field(
            description=(
                "The portfolio organizer settings to use as an underlying schema of "
                "portfolios. The 'Default' schema is used by default."
            ),
        ),
        SettingsTypeMetaData[str | int | PortfolioOrganizerSettings](
            references=PortfolioOrganizerSettings
        ),
    ]
    ffill: Literal["no-ffill", "ffill-with-drift"] = "no-ffill"
    unpack: Literal["no-unpack", "unpack"] = "no-unpack"

    @classmethod
    def from_source(
        cls: type["PortfolioSettings"],
        source: str,
        ffill: Literal["no-ffill", "ffill-with-drift"] = "no-ffill",
        unpack: Literal["no-unpack", "unpack"] = "no-unpack",
        dataset: str | None = None,
    ) -> "PortfolioSettings":
        """Create portfolio settings from a source.

        Parameters
        ----------
        source : str
            The source for enabled portfolios.
        ffill : Literal["no-ffill", "ffill-with-drift"], default="no-ffill"
            The forward fill option.
        unpack : Literal["no-unpack", "unpack"], default="no-unpack"
            The unpack option.
        dataset : str | None, default=None
            The dataset name, defaults to None.

        Returns
        -------
        PortfolioSettings
            The created portfolio settings.
        """
        return cls(
            portfolio_schema=PortfolioOrganizerSettings(
                enabled_portfolios=source, dataset=dataset
            ),
            ffill=ffill,
            unpack=unpack,
        )


class PortfolioSettingsMenu(
    SettingsMenu[PortfolioSettings], frozen=True, extra="forbid"
):
    """Specifies the set of available options that can be used to create portfolio settings."""

    sources: list[str] = Field(
        description=(
            "The available sources (i.e. user uploaded portfolios or system "
            "uploaded portfolios)."
        ),
        default_factory=list,
    )

    schemas: list[str] = Field(
        description=(
            "The available schemas (i.e. names from the portfolio organizer)."
        ),
        default_factory=list,
    )

    def describe(self, settings: PortfolioSettings | None = None) -> str:
        """Describe the available options or settings.

        Parameters
        ----------
        settings : PortfolioSettings | None, default=None
            The settings to describe, or None to describe available options.

        Returns
        -------
        str
            A description of the available options or settings.
        """
        if settings is None:
            return (
                f"Sources: {', '.join(self.sources)}\n"
                f"Schemas: {', '.join(self.schemas)}\n"
                "Forward Fill Options: 'no-ffill', 'ffill-with-drift'\n"
                "Unpack Options: 'no-unpack', 'unpack"
            )
        else:
            return f"Forward Fill: {settings.ffill}\nUnpack: {settings.unpack}"

    def validate_settings(self, settings: PortfolioSettings) -> None:
        """Validate the portfolio settings.

        Parameters
        ----------
        settings : PortfolioSettings
            The settings to validate.

        Raises
        ------
        ValueError
            If the schema is invalid or source is not found.
        """
        s = settings.portfolio_schema
        if isinstance(s, str) and s not in self.schemas:
            raise ValueError(
                f"Invalid schema: {settings.portfolio_schema}. "
                f"Available schemas are: {', '.join(self.schemas)}"
            )

        if isinstance(s, PortfolioOrganizerSettings):
            if isinstance(s.enabled_portfolios, str):
                if s.enabled_portfolios not in self.sources:
                    raise ValueError(
                        f"Invalid source: {s.enabled_portfolios}. "
                        f"Available sources: {', '.join(self.sources)}"
                    )
            else:
                invalid_sources = [
                    source
                    for source in s.enabled_portfolios.values()
                    if source not in self.sources
                ]
                if invalid_sources:
                    raise ValueError(
                        f"Invalid sources: {invalid_sources}. "
                        f"Available sources: {', '.join(self.sources)}"
                    )
