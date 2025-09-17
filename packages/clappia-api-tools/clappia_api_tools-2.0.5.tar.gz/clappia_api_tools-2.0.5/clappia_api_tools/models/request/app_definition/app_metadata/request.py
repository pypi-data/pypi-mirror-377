from pydantic import BaseModel, Field, field_validator, model_validator
from ....json_serialized import JsonSerializableMixin
from typing import List, Optional, Literal
import re

HEX_COLOR_REGEX = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

class ExternalStatusDefinition(BaseModel, JsonSerializableMixin):
    name: str = Field(..., min_length=1, description="Name of the status")
    color: str = Field(..., min_length=1, description="Color of the status in hex format")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError("Status color must be a valid hex code (e.g. #000000 or #FFF)")
        return v

class UpdateAppMetadataRequest(BaseModel, JsonSerializableMixin):
    app_name: Optional[str] = Field(None, description="Name of the app, < 30 chars")
    app_description: Optional[str] = Field(None, description="Description of the app, < 100 chars")
    is_analytics_enabled: Optional[bool] = Field(None, description="Whether analytics is enabled")
    requires_authentication: Optional[bool] = Field(None, description="Whether authentication is required")
    allow_embedding: Optional[bool] = Field(None, description="Whether embedding is allowed")
    require_auth_for_submissions: Optional[bool] = Field(None, description="Whether authentication is required for submissions")
    can_user_submit: Optional[bool] = Field(None, description="Whether user can submit")
    can_user_save_draft: Optional[bool] = Field(None, description="Whether user can save draft")
    statuses: Optional[List[ExternalStatusDefinition]] = Field(None, min_length=1, description="Statuses of the app, they can be used to review submissions. Example: [{'name': 'Pending', 'color': '#000000'}, {'name': 'Approved', 'color': '#000000'}]")
    post_submission_message_text: Optional[str] = Field(None, description="Post submission message text, can contain field references. Example: 'Thank you for submitting your form. The submission id is {submissionId}.'")
    submit_button_label: Optional[str] = Field(None, description="Submit button label")
    submission_display_name: Optional[str] = Field(None, description="Custom submission display name, < 30 chars")
    allow_viewing_submissions: Optional[bool] = Field(None, description="Whether viewing submissions is allowed")
    allow_submit_another: Optional[bool] = Field(None, description="Whether submitting another is allowed")
    allow_printing_submissions: Optional[bool] = Field(None, description="Whether printing submissions is allowed")
    save_draft_button_label: Optional[str] = Field(None, description="Label for save draft button")
    discard_draft_button_label: Optional[str] = Field(None, description="Label for discard draft button")
    print_submission_button_label: Optional[str] = Field(None, description="Label for print submission button")
    view_submissions_button_label: Optional[str] = Field(None, description="Label for view submissions button")
    submit_another_button_label: Optional[str] = Field(None, description="Label for submit another button")
    submission_view_mode: Optional[Literal["modal", "rightPanel"]] = Field(None, description="Submission view mode (modal or rightPanel)")
    default_app_view: Optional[Literal["appHome", "analytics", "submissions"]] = Field(None, description="Default app view (appHome, analytics, submissions)")

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 30:
            raise ValueError("app_name must be less than 30 characters")
        return v

    @field_validator("app_description")
    @classmethod
    def validate_app_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 100:
            raise ValueError("app_description must be less than 100 characters")
        return v

    @field_validator("submission_display_name")
    @classmethod
    def validate_submission_display_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) == 0:
                raise ValueError("submission_display_name cannot be empty")
            if len(v) > 30:
                raise ValueError("submission_display_name must be less than 30 characters")
        return v

    @model_validator(mode='after')
    def validate_statuses_unique(self) -> 'UpdateAppMetadataRequest':
        if self.statuses:
            names = [s.name for s in self.statuses]
            if len(names) != len(set(names)):
                raise ValueError("statuses must not contain duplicate names")
        return self