import os
import asyncio
from typing import Any
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from app.services.resume_optimizer import StandardATSResumeContent
from app.services.storage import get_storage_service

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


async def render_resume_to_pdf_bytes(resume_data: Any) -> bytes:
    """
    Renderiza o template HTML via Jinja2 e compila em PDF de alta fidelidade
    usando Playwright headless (perfeito para leitura e parsing de robôs ATS).
    """
    template = jinja_env.get_template("ats_resume.html")
    html_content = template.render(resume=resume_data.model_dump())

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = await page.pdf(
            format="A4",
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"},
            print_background=True
        )
        await browser.close()
        return pdf_bytes


def generate_and_save_tailored_pdf(
    resume_data: Any,
    job_id: int,
    candidate_id: int
) -> str:
    """
    Executa a compilação do PDF e salva no Storage Service (Local ou S3).
    Retorna a URL/path do PDF gerado.
    """
    pdf_bytes = asyncio.run(render_resume_to_pdf_bytes(resume_data))
    filename = f"curriculo_job_{job_id}_cand_{candidate_id}.pdf"
    
    storage = get_storage_service()
    file_url = storage.upload_file(pdf_bytes, filename)
    return file_url
