import logging
import urllib.parse
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LinkedInJobsScraper:
    """
    Coletor de vagas públicas do LinkedIn (Guest / Public API).
    Não exige login nem cookies para vagas abertas.
    """

    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def search_jobs(
        self,
        keywords: str = "estagio python",
        location: str = "Brasil",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca vagas recentes no LinkedIn usando a API pública de busca.
        """
        # Limpeza básica do termo para o padrão da API de vagas do LinkedIn
        clean_keywords = keywords.replace("estágio", "estagio").replace("TI", "software").strip()
        params = {
            "keywords": clean_keywords or "estagio software python",
            "location": location if location != "ALL" else "Brasil",
            "start": 0,
            "f_TPR": "r2592000", # Últimos 30 dias
        }

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        logger.info(f"Buscando vagas no LinkedIn: {url}")

        jobs = []
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=20.0, follow_redirects=True) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    logger.warning(f"LinkedIn retornou status {res.status_code}")
                    return []

                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all("li")

                for card in cards[:limit]:
                    title_elem = card.find("h3", class_="base-search-card__title")
                    company_elem = card.find("h4", class_="base-search-card__subtitle")
                    location_elem = card.find("span", class_="job-search-card__location")
                    link_elem = card.find("a", class_="base-card__full-link")

                    if title_elem and company_elem:
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        loc = location_elem.text.strip() if location_elem else "Brasil"
                        job_url = link_elem["href"].split("?")[0] if link_elem and "href" in link_elem.attrs else ""

                        # Identifica modalidade no título/local
                        workplace = "Remoto" if "remoto" in title.lower() or "remoto" in loc.lower() else "Híbrido" if "híbrido" in loc.lower() else "Presencial"

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "workplace_type": workplace,
                            "job_url": job_url or f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(title)}",
                            "source": "LinkedIn",
                            "salary": "A combinar",
                            "raw_description": (
                                f"Vaga coletada do LinkedIn: {title} na empresa {company}. "
                                f"Localidade: {loc}. Requisitos e candidatura disponíveis no link original."
                            )
                        })

                logger.info(f"Encontradas {len(jobs)} vagas públicas no LinkedIn.")
                return jobs

        except Exception as e:
            logger.error(f"Erro ao raspar vagas do LinkedIn: {e}")
            return []
