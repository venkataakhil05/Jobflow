import asyncio
import httpx


JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 10.0


async def fetch_jobs(count: int = 20):
    params = {
        "count": count
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT
            ) as client:

                response = await client.get(
                    JOBICY_URL,
                    params=params
                )

                response.raise_for_status()

                data = response.json()

                return data.get("jobs", [])

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError
        ) as error:

            print(
                f"Jobicy request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt == MAX_RETRIES:
                raise

            await asyncio.sleep(2 ** (attempt - 1))