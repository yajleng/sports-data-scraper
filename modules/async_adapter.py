import httpx, asyncio

async def fetch_async(url, headers=None, params=None):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()
