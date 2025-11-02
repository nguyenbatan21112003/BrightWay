import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from ..models.schemas import TestGenerationResult, TestCase, TestData
from .rule_engine import generate_basic_testcases  # fallback khi LLM fail

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # hoặc gpt-4o-mini


def _build_prompt(project_name: str, scenario: str, requirements: str | None):
    return f"""
You are a senior QA engineer. Convert the following software scenario into TEST CASES and TEST DATA.
Return **ONLY** JSON with 2 keys: "testcases" and "test_data".

Project: {project_name}
Scenario: {scenario}
Requirements: {requirements or "N/A"}

JSON schema:
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
    {{
      "field": "string",
      "value": "string"
    }}
  ]
}}

Rules:
- Steps must be short and actionable.
- Expected must be clear and verifiable.
- IDs must be sequential (TC001, TC002, ...).
- If requirements mention validation or payment -> create at least 3 testcases.
"""


def generate_from_scenario(project_name: str, scenario: str, requirements: str | None = None) -> TestGenerationResult:
    try:
        prompt = _build_prompt(project_name, scenario, requirements)

        # gọi LLM thật
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You generate QA testcases from user scenarios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        content = resp.choices[0].message.content.strip()
        # LLM trả về JSON dạng text → parse
        data = json.loads(content)

        testcases = [
            TestCase(
                id=tc.get("id", f"TC{i+1:03d}"),
                title=tc.get("title", "No title"),
                steps=tc.get("steps", []),
                expected=tc.get("expected", "")
            )
            for i, tc in enumerate(data.get("testcases", []))
        ]

        test_data = [
            TestData(
                field=d.get("field", ""),
                value=d.get("value", "")
            )
            for d in data.get("test_data", [])
        ]

        return TestGenerationResult(testcases=testcases, test_data=test_data)

    except Exception as e:
        # fallback về rule nếu LLM lỗi / hết quota
        print("LLM error, fallback to rule:", e)
        basic_tcs = generate_basic_testcases(project_name, scenario, requirements)
        fallback_data = [
            TestData(field="username", value="fallback_user"),
            TestData(field="password", value="fallback_pass"),
        ]
        return TestGenerationResult(testcases=basic_tcs, test_data=fallback_data)