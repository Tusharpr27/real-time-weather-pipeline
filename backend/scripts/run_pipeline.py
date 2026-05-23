import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.processor.pipeline import get_processing_pipeline

async def main():
    pipeline = await get_processing_pipeline()
    print('Running data processing pipeline...')
    success = await pipeline.process_recent_data()
    print('Processing completed. Success =', success)

if __name__ == '__main__':
    asyncio.run(main())
