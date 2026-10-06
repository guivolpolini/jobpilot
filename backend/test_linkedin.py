import asyncio
import json
from app.services.linkedin_scraper import LinkedInJobsScraper

async def run_test():
    scraper = LinkedInJobsScraper()
    jobs = await scraper.search_jobs("estagio python", "Brasil", 5)
    print(f"Total raspado: {len(jobs)}")
    for j in jobs:
        print(f"- {j['title']} ({j['company']})")

if __name__ == "__main__":
    asyncio.run(run_test())
