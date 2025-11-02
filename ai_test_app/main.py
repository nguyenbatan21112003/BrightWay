from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from .models.schemas import TestRequest, TestGenerationResult, RenderReportRequest
from .system.ai_generator import generate_from_scenario
from .reports.report_generator import render_report_to_html
from pathlib import Path

app = FastAPI(title="BrightWay AI Testcase Generator", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(BASE_DIR / "frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/generate_testcases", response_model=TestGenerationResult)
def generate_testcases(req: TestRequest):
    """API 1: Sinh testcase và testdata từ kịch bản"""
    try:
        result = generate_from_scenario(
            project_name=req.project_name,
            scenario=req.scenario,
            requirements=req.requirements
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi sinh testcase: {str(e)}")


@app.post("/render_report")
def render_report_api(req: RenderReportRequest):
    """API 2: Render report HTML từ testcases và test_data"""
    try:
        report_path = render_report_to_html(
            project_name=req.project_name,
            scenario=req.scenario,
            ai_model=req.ai_model or "mock-ai",
            testcases=req.testcases,
            test_data=req.test_data
        )
        
        return {
            "message": "Render report thành công",
            "report_path": report_path.replace("\\", "/"),
            "filename": Path(report_path).name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi render report: {str(e)}")


@app.get("/download_report")
def download_report(path: str):
    """API 3: Tải file report đã render"""
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file báo cáo")
    return FileResponse(path, media_type="text/html", filename=file_path.name)