"""Data models for QATest test cases."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TestStep(BaseModel):
    """Model for a test step."""

    action: str = Field(..., description="The action to perform")
    expected_result: str = Field(..., description="The expected result of the action")

    @field_validator('action')
    @classmethod
    def validate_action_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("action cannot be empty")
        return v.strip()
    
    @field_validator('expected_result')
    @classmethod
    def strip_expected_result(cls, v: str) -> str:
        # Just strip whitespace, allow empty values
        return v.strip() if v else ""


class TestCase(BaseModel):
    """Model for a test case."""

    id: int = Field(..., description="Unique identifier for the test case")
    title: str = Field(..., description="Title of the test case")
    description: Optional[str] = Field(None, description="Description of the test case")
    preconditions: Optional[str] = Field(None, description="Preconditions for the test case")
    steps: List[TestStep] = Field(..., description="List of test steps")
    directory_path: str = Field(..., description="Directory path relative to test cases root")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Test case ID must be a positive integer")
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator('directory_path')
    @classmethod
    def validate_directory_path(cls, v: str) -> str:
        # Allow empty string for root-level files, but strip whitespace
        if v is None:
            raise ValueError("Directory path is required")
        return v.strip()


    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 442,
                "title": "Default view page",
                "description": "Test the default view of the accounts page",
                "preconditions": "User is logged in",
                "steps": [
                    {
                        "action": "Tap on Settings tab",
                        "expected_result": "Settings tab is opened"
                    },
                    {
                        "action": "Press on the company name",
                        "expected_result": "The Accounts list is displayed"
                    }
                ]
            }
        }
    }
