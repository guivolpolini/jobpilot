from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel


class FormFillPreview(BaseModel):
    """Dados mapeados que serão preenchidos para revisão humana prévia"""
    platform: str
    target_url: str
    full_name: str
    email: str
    phone: str
    linkedin_url: str
    github_url: str
    resume_path: str
    custom_fields: Dict[str, Any] = {}
    requires_human_captcha: bool = False


class BaseJobBoardAdapter(ABC):
    """Classe base para adaptadores de preenchimento de candidaturas (Gupy, Greenhouse, Lever, etc.)"""

    @abstractmethod
    async def extract_form_fields(self, page_url: str) -> Dict[str, Any]:
        """Inspeciona a página da vaga para mapear campos do formulário"""
        pass

    @abstractmethod
    def generate_fill_preview(self, candidate_data: Dict[str, Any], resume_path: str) -> FormFillPreview:
        """Gera o preview para aprovação do usuário antes do envio"""
        pass

    @abstractmethod
    async def execute_form_submission(self, preview_data: FormFillPreview, headless: bool = False) -> Dict[str, Any]:
        """Executa a automação no navegador com Playwright após confirmação do usuário"""
        pass
