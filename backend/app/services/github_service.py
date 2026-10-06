import re
import json
import base64
import logging
import urllib.request
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def fetch_github_profile_data(username: str = "guivolpolini") -> Dict[str, Any]:
    """
    Busca automaticamente repositórios reais, bio e projetos do GitHub
    para enriquecer o currículo do candidato e gerar provas concretas de competência.
    """
    headers = {"User-Agent": "JobPilot-Agent"}
    profile_info = {
        "username": username,
        "github_url": f"https://github.com/{username}",
        "profile_readme": "",
        "highlighted_projects": [],
        "languages_found": set(),
        "topics_found": set()
    }

    # 1. Profile README (onde ficam bio, links, certificações e descrições do perfil)
    try:
        url = f"https://api.github.com/repos/{username}/{username}/readme"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            profile_info["profile_readme"] = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Não foi possível obter README principal do perfil GitHub: {e}")

    # 2. Lista de repositórios do usuário
    try:
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=20"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
            for repo in repos:
                if repo.get("fork"):
                    continue
                name = repo.get("name")
                desc = repo.get("description") or ""
                lang = repo.get("language")
                html_url = repo.get("html_url")
                topics = repo.get("topics") or []

                if lang:
                    profile_info["languages_found"].add(lang)
                for t in topics:
                    profile_info["topics_found"].add(t)

                profile_info["highlighted_projects"].append({
                    "name": name,
                    "description": desc,
                    "language": lang,
                    "url": html_url
                })
    except Exception as e:
        logger.warning(f"Não foi possível listar repositórios do GitHub: {e}")

    profile_info["languages_found"] = list(profile_info["languages_found"])
    profile_info["topics_found"] = list(profile_info["topics_found"])
    return profile_info
