"""View models for SFMC email templates (HTML, text, subject line, preheader)."""

from typing import Any

from pydantic import BaseModel, Field

from pysfmc.models.assets.blocks import Slot
from pysfmc.models.base import SFMC_MODEL_CONFIG


class BaseView(BaseModel):
    """Base view model with common properties."""

    @staticmethod
    def default_factory_data():
        return {"email": {"options": {"generateFrom": None}}}

    model_config = SFMC_MODEL_CONFIG

    thumbnail: dict[str, Any] = Field(default_factory=dict)
    available_views: list[str] = Field(default_factory=list, alias="availableViews")
    data: dict[str, Any] | None = Field(default=None)
    model_version: int | None = Field(default=None, alias="modelVersion")
    content_type: str | None = Field(None, alias="contentType")
    meta: dict[str, Any] = Field(default_factory=dict)

    # Optional content in base class
    content: str | None = Field(default=None, description="View content")
    template: dict[str, Any] | None = None
    slots: dict[str, Slot] | None = Field(default=None, description="Slots in the view")

    @classmethod
    def default_view(cls) -> "BaseView":
        return cls(data=BaseView.default_factory_data(), modelVersion=2)


class HtmlView(BaseView):
    """HTML view with template and slots support."""

    # Override content to make it mandatory
    content: str = Field(..., description="HTML content")  # Required field
    template: dict[str, Any] = Field(default_factory=dict)
    slots: dict[str, Slot] = Field(default_factory=dict)


if __name__ == "__main__":
    print(BaseView().model_dump())

    print(HtmlView(content="").model_dump())
