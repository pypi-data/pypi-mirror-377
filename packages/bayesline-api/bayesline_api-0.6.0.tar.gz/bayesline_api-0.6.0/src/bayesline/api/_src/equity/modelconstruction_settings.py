import os
from typing import Literal

from pydantic import Field, NonNegativeFloat, NonPositiveFloat

from bayesline.api._src.registry import Settings, SettingsMenu

WeightingScheme = Literal["SqrtCap", "InvIdioVar"]


class ModelConstructionSettings(Settings):
    """Defines settings to build a factor risk model."""

    currency: str = Field(
        description="The currency of the factor risk model.",
        default="USD",
        examples=["USD", "EUR"],
    )
    weights: WeightingScheme = Field(
        description="The regression weights used for the factor risk model.",
        default="SqrtCap",
        examples=["SqrtCap", "InvIdioVar"],
    )
    alpha: NonNegativeFloat = Field(
        description="The ridge-shrinkage factor for the factor risk model.",
        default=0.0,
    )
    alpha_overrides: dict[str, NonNegativeFloat] = Field(
        description=(
            "The alpha override for the factor risk model. The keys are the factor "
            "names and the values are the alpha overrides."
        ),
        default_factory=dict,
    )
    return_clip_bounds: tuple[NonPositiveFloat | None, NonNegativeFloat | None] = Field(
        description="The bounds for the return clipping.",
        default=(-0.1, 0.1),
        examples=[(-0.1, 0.1), (None, None)],
    )


class ModelConstructionSettingsMenu(
    SettingsMenu[ModelConstructionSettings], frozen=True, extra="forbid"
):
    """Defines available modelconstruction settings to build a factor risk model."""

    weights: list[WeightingScheme] = Field(
        description="""
        The available regression weights that can be used for the factor risk model.
        """,
    )

    def describe(self, settings: ModelConstructionSettings | None = None) -> str:
        """Describe the available weights or settings.

        Parameters
        ----------
        settings : ModelConstructionSettings | None, default=None
            The settings to describe, or None to describe available weights.

        Returns
        -------
        str
            A description of the available weights or settings.
        """
        if settings is not None:
            lines = [
                f"Currency: {settings.currency}",
                f"Weights: {settings.weights}",
                f"Alpha: {settings.alpha}",
            ]
            if settings.alpha_overrides:
                lines.append("Alpha Overrides:")
                lines.extend(
                    f"    {k}: {v:.6f}" for k, v in settings.alpha_overrides.items()
                )
            lines.append(f"Return Clip Bounds: {settings.return_clip_bounds}")

        else:
            lines = [f"Weights: {', '.join(self.weights)}"]
        return os.linesep.join(lines)

    def validate_settings(self, settings: ModelConstructionSettings) -> None:
        """Validate the model construction settings.

        Parameters
        ----------
        settings : ModelConstructionSettings
            The settings to validate.

        Raises
        ------
        ValueError
            If the weights are not available.
        """
        if settings.weights not in self.weights:
            raise ValueError(f"Invalid weights: {settings.weights}")
        # TODO add validation for currencies, overrides, etc.
