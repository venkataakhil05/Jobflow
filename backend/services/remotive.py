import httpx


REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

REQUEST_TIMEOUT = 10.0


async def fetch_jobs(count: int = 20):
    """
    Fetch jobs from Remotive as the fallback source.
    """

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT
    ) as client:

        response = await client.get(REMOTIVE_URL)

        response.raise_for_status()

        data = response.json()

        jobs = data.get("jobs", [])

        return jobs[:count]
    

import asyncio


async def main():
    jobs = await fetch_jobs(5)

    print(f"Remotive jobs received: {len(jobs)}")

    for job in jobs[:5]:
        print(
            job.get("title"),
            "|",
            job.get("company_name"),
            "|",
            job.get("url")
        )


if __name__ == "__main__":
    asyncio.run(main())