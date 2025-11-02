from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from .models.schemas import TestRequest
from .system.ai_generator import generate_from_scenario
from .reports.report_generator import render_report_to_html
from pathlib import Path

app = FastAPI(title="AI Testcase Generator", version="0.1.0")

# Xác định thư mục gốc của ứng dụng
BASE_DIR = Path(__file__).resolve().parent

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(BASE_DIR / "frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/generate_test")
def generate_test(req: TestRequest):
    try:
        # 1. gọi SYSTEM để sinh testcase + testdata
        result = generate_from_scenario(
            project_name=req.project_name,
            scenario=req.scenario,
            requirements=req.requirements
        )
        # 2. render ra report HTML
        report_path = render_report_to_html(
            project_name=req.project_name,
            scenario=req.scenario,
            ai_model=req.ai_model or "mock-ai",
            testcases=result.testcases,
            test_data=result.test_data
        )

        # 3. trả về file luôn (hoặc trả về path)
        return {
            "message": "Sinh testcase thành công",
            "report_path": report_path.replace("\\", "/"),
            "testcases_count": len(result.testcases),
            "test_data_count": len(result.test_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download_report")
def download_report(path: str):
    """Cho tải file đã render"""
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file báo cáo")
    return FileResponse(path, media_type="text/html", filename=file_path.name)