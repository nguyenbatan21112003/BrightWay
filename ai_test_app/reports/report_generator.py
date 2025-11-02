from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "output_reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def render_report_to_html(project_name: str, scenario: str, ai_model: str, testcases, test_data) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report_template.html")

    html_content = template.render(
        project_name=project_name,
        scenario=scenario,
        ai_model=ai_model,
        testcases=testcases,
        test_data=test_data,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Lưu ra file
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_path = OUTPUT_DIR / filename
    output_path.write_text(html_content, encoding="utf-8")

    # Trả về path để FastAPI gửi lại cho client
    return str(output_path)
