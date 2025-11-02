from pydantic import BaseModel
from typing import List, Optional


class TestRequest(BaseModel):
    project_name: str
    scenario: str
    requirements: Optional[str] = None
    ai_model: Optional[str] = "mock-ai"


class TestCase(BaseModel):
    id: str
    title: str
    steps: List[str]
    expected: str


class TestData(BaseModel):
    field: str
    value: str


class TestGenerationResult(BaseModel):
    testcases: List[TestCase]
    test_data: List[TestData]
