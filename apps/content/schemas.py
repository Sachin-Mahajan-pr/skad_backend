from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

class LinkField(BaseModel):
    """
    Button and link schema per Doc 2 Page 15:
    Validation: external URLs must be https; entity/page targets must exist.
    """
    label: str = Field(..., max_length=60)
    kind: Literal["page", "entity", "external", "anchor", "file"] = "page"
    target: str
    open_in_new_tab: bool = False

    @model_validator(mode="after")
    def validate_external_url(self):
        if self.kind == "external" and not self.target.startswith("https://"):
            raise ValueError("External URLs must use secure HTTPS protocol.")
        return self

class MediaRef(BaseModel):
    url: str
    alt: str = ""
    caption: Optional[str] = None

class HeroContent(BaseModel):
    headline_lines: List[str] = Field(
        default_factory=lambda: [
            "BUILDING BUSINESSES.",
            "CREATING BRANDS.",
            "SHAPING THE FUTURE."
        ],
        min_length=1,
        max_length=4
    )
    supporting_copy: str = Field(
        default=(
            "SKAD GROUP is a diversified business group building companies, brands, "
            "technology platforms and entrepreneurial ventures across markets."
        ),
        max_length=300
    )
    primary_cta: LinkField = Field(default_factory=lambda: LinkField(
        label="EXPLORE THE GROUP", kind="page", target="about"
    ))
    secondary_cta: Optional[LinkField] = Field(default_factory=lambda: LinkField(
        label="PARTNER WITH SKAD", kind="page", target="partner-with-skad"
    ))
    show_infinity_animation: bool = True
    image: Optional[MediaRef] = None

class GroupIntroContent(BaseModel):
    lead_statement: str = Field(default="BUILD • CONNECT • SCALE", max_length=240)
    description: str = (
        "We build scalable businesses, connect global capabilities, and scale "
        "sustainable value across industries."
    )
    pillars: List[Dict[str, Any]] = Field(default_factory=list)

class EcosystemContent(BaseModel):
    title: str = "Interactive SKAD Ecosystem"
    description: Optional[str] = "Visual map of Group, Companies, Brands, Platforms, and Impact Foundation."
    show_graph: bool = True

class ContactCtaContent(BaseModel):
    heading: str = "Partner With SKAD"
    supporting_text: str = "Connect with our leadership across commerce, trade, and strategic partnerships."
    cta_button: LinkField = Field(default_factory=lambda: LinkField(
        label="START A CONVERSATION", kind="page", target="contact"
    ))

class AtAGlanceContent(BaseModel):
    title: str = "At a Glance"
    items: List[Dict[str, str]] = Field(default_factory=list)

class ValuePillarsContent(BaseModel):
    title: str = "How We Create Value"
    pillars: List[Dict[str, str]] = Field(default_factory=list)

class RichTextContent(BaseModel):
    headline: Optional[str] = None
    body: str

class ImageTextContent(BaseModel):
    headline: str
    body: str
    image: Optional[MediaRef] = None
    cta: Optional[LinkField] = None

SECTION_SCHEMAS = {
    "hero": HeroContent,
    "group_intro": GroupIntroContent,
    "ecosystem": EcosystemContent,
    "contact": ContactCtaContent,
    "cta_band": ContactCtaContent,
    "at_a_glance": AtAGlanceContent,
    "value_pillars": ValuePillarsContent,
    "rich_text": RichTextContent,
    "image_text": ImageTextContent,
}

def validate_section_content(section_type: str, content: dict) -> dict:
    """
    Validates JSON content for a section against its registered Pydantic schema.
    If valid, returns the validated model dictionary; otherwise raises ValidationError.
    """
    schema = SECTION_SCHEMAS.get(section_type)
    if not schema:
        # Flexible for other section types without rigid schemas
        return content
    
    validated = schema.model_validate(content or {})
    return validated.model_dump()
