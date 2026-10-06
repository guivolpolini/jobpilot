import os
import logging
from typing import Dict, Any, List
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

COLUMNS = [
    "ID Vaga",
    "Empresa",
    "Cargo",
    "Match %",
    "Link da Vaga",
    "Currículo ATS (PDF)",
    "Status",
    "Link de Disparo (1 Clique)",
    "Data Atualização"
]


class GoogleSheetsService:
    def __init__(self):
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.sheet_name = settings.GOOGLE_SHEET_NAME
        self.client = None
        self._authenticate()

    def _authenticate(self):
        if not os.path.exists(self.credentials_file):
            logger.warning(f"Google credentials file '{self.credentials_file}' não encontrado. Modo simulação ativo.")
            return

        try:
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=SCOPES)
            self.client = gspread.authorize(creds)
        except Exception as e:
            logger.error(f"Erro ao autenticar no Google Sheets: {e}")

    def sync_job_row(
        self,
        job_id: int,
        company: str,
        role: str,
        match_score: int,
        job_url: str,
        resume_pdf_url: str,
        status: str = "Pronto para Envio",
        base_api_url: str = "http://localhost:8000"
    ):
        """
        Adiciona ou atualiza linha na planilha do Google Sheets com o link de 1 clique.
        """
        one_click_trigger_url = f"{base_api_url}/api/v1/apply/{job_id}"
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")

        row_data = [
            str(job_id),
            company,
            role,
            f"{match_score}%",
            job_url,
            resume_pdf_url or "Pendente",
            status,
            one_click_trigger_url,
            now_str
        ]

        if not self.client:
            logger.info(f"[SIMULAÇÃO PLANILHA] Linha pronta para sync: {row_data}")
            return row_data

        try:
            sheet = self.client.open(self.sheet_name).sheet1
            # Se for a primeira linha, garante cabeçalhos
            existing_records = sheet.get_all_values()
            if not existing_records:
                sheet.append_row(COLUMNS)

            # Verifica se já existe a vaga pelo ID para atualizar ou criar
            cell = sheet.find(str(job_id)) if existing_records else None
            if cell:
                row_idx = cell.row
                sheet.update(f"A{row_idx}:I{row_idx}", [row_data])
                logger.info(f"Linha {row_idx} atualizada no Google Sheets para Vaga {job_id}")
            else:
                sheet.append_row(row_data)
                logger.info(f"Nova linha adicionada no Google Sheets para Vaga {job_id}")

            return row_data
        except Exception as e:
            logger.error(f"Falha ao sincronizar com Google Sheets: {e}")
            return row_data
