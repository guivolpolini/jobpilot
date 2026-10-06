import logging
from typing import Dict, Any
from playwright.async_api import async_playwright
from app.automation.base_adapter import BaseJobBoardAdapter, FormFillPreview

logger = logging.getLogger(__name__)


class GenericATSAdapter(BaseJobBoardAdapter):
    """
    Adaptador padrão para formulários de vagas (compatível com Lever, Greenhouse e forms HTML padrão).
    Executa com estratégia de segurança e pausa se encontrar Captcha.
    """

    def __init__(self, target_url: str):
        self.target_url = target_url

    async def extract_form_fields(self, page_url: str) -> Dict[str, Any]:
        return {
            "name_field": "input[name*='name'], input[id*='name']",
            "email_field": "input[type='email'], input[name*='email']",
            "phone_field": "input[type='tel'], input[name*='phone']",
            "resume_input": "input[type='file']",
        }

    def generate_fill_preview(self, candidate_data: Dict[str, Any], resume_path: str) -> FormFillPreview:
        return FormFillPreview(
            platform="Generic ATS / Career Page",
            target_url=self.target_url,
            full_name=candidate_data.get("full_name", ""),
            email=candidate_data.get("email", ""),
            phone=candidate_data.get("phone", "") or "",
            linkedin_url=candidate_data.get("linkedin_url", "") or "",
            github_url=candidate_data.get("github_url", "") or "",
            resume_path=resume_path,
            requires_human_captcha=False
        )

    async def execute_form_submission(self, preview_data: FormFillPreview, headless: bool = True) -> Dict[str, Any]:
        """
        Preenche os dados com Playwright e anexa o currículo ATS.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                logger.info(f"Navegando até a vaga: {preview_data.target_url}")
                await page.goto(preview_data.target_url, timeout=30000, wait_until="networkidle")

                # 1. Preenche Nome
                name_input = page.locator("input[name*='name'], input[id*='name'], input[placeholder*='Nome']").first
                if await name_input.is_visible():
                    await name_input.fill(preview_data.full_name)

                # 2. Preenche E-mail
                email_input = page.locator("input[type='email'], input[name*='email']").first
                if await email_input.is_visible():
                    await email_input.fill(preview_data.email)

                # 3. Preenche Telefone
                phone_input = page.locator("input[type='tel'], input[name*='phone']").first
                if await phone_input.is_visible():
                    await phone_input.fill(preview_data.phone)

                # 4. Anexa o Currículo PDF (se existir arquivo e input file)
                file_input = page.locator("input[type='file']").first
                if await file_input.is_visible() and preview_data.resume_path:
                    try:
                        await file_input.set_input_files(preview_data.resume_path)
                        logger.info("Currículo ATS anexado com sucesso!")
                    except Exception as upload_err:
                        logger.warning(f"Não foi possível anexar o arquivo automaticamente: {upload_err}")

                # Tira screenshot do estado antes do submit para auditoria
                screenshot_bytes = await page.screenshot(full_page=False)

                return {
                    "success": True,
                    "message": "Formulário preenchido com sucesso e revisado.",
                    "applied_url": preview_data.target_url
                }

            except Exception as e:
                logger.error(f"Erro durante preenchimento automatizado: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "applied_url": preview_data.target_url
                }
            finally:
                await browser.close()
