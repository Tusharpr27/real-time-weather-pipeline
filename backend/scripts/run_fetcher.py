import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fetcher.data_fetcher import get_fetcher

async def main():
    fetcher = await get_fetcher()
    print('Starting one-off fetch cycle...')
    success = await fetcher.fetch_weather_for_all_locations()
    print('Fetch completed. Success =', success)

if __name__ == '__main__':
    asyncio.run(main())
