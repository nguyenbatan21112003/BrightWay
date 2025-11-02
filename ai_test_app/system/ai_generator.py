import os
import json
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

from ..models.schemas import TestGenerationResult, TestCase, TestData
from .rule_engine import generate_basic_testcases  # fallback

load_dotenv()

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


def _build_prompt(project_name: str, scenario: str, requirements: Optional[str]):
    # System prompt is now part of the main prompt for Gemini
    return f"""Bạn là một kỹ sư QA/kiểm thử cao cấp. 
Nhiệm vụ của bạn là tạo TEST CASES và TEST DATA cho kịch bản người dùng sau đây.
Chỉ trả về JSON hợp lệ, không giải thích gì thêm.

Project: {project_name}
Scenario: {scenario}
Requirements: {requirements or "N/A"}

JSON format:
{{
  "testcases": [
    {{
      "id": "TC001",
      "title": "string",
      "steps": ["step 1", "step 2"],
      "expected": "string"
    }}
  ],
  "test_data": [
    {{"field": "string", "value": "string"}}
  ]
}}

Rules:
- Use Vietnamese for title/steps/expected.
- IDs must be sequential (TC001, TC002, ...).
- If scenario is about form/payment/auth → create at least 4 testcases.
- Steps must be short, clear, executable.
"""


def generate_from_scenario(
    project_name: str,
    scenario: str,
    requirements: Optional[str] = None
) -> TestGenerationResult:
    try:
        prompt = _build_prompt(project_name, scenario, requirements)

        # Call the Gemini API
        model = genai.GenerativeModel(DEFAULT_MODEL)
        resp = model.generate_content(prompt)

        # The response from Gemini might be wrapped in ```json ... ```, so we need to extract it.
        content = resp.text.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()

        print("AI RAW:", content)
        data = json.loads(content)

        testcases = [
            TestCase(
                id=tc.get("id", f"TC{i+1:03d}"),
                title=tc.get("title", "Chưa có tiêu đề"),
                steps=tc.get("steps", []),
                expected=tc.get("expected", "")
            )
            for i, tc in enumerate(data.get("testcases", []))
        ]

        test_data = [
            TestData(field=d.get("field", ""), value=d.get("value", ""))
            for d in data.get("test_data", [])
        ]

        return TestGenerationResult(testcases=testcases, test_data=test_data)

    except Exception as e:
        # Fallback to rule-based generation if LLM fails
        print(f"LLM error: {e}")
        fallback_tcs = generate_basic_testcases(project_name, scenario, requirements)
        return TestGenerationResult(
            testcases=fallback_tcs,
            test_data=[
                TestData(field="username", value="fallback_user"),
                TestData(field="password", value="fallback_pass"),
            ]
        )