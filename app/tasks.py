import asyncio
import uuid

from app.db.config import SessionLocal
from app.db.models import GenerationORM
from app.models import Status

session = SessionLocal()


async def generate_image_task(generation_id: uuid.UUID) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            generation = await session.get(GenerationORM, generation_id)
            if not generation:
                raise ValueError(f"Generation with ID {generation_id} not found")
            generation.status = Status.IN_PROGRESS

        try:
            await asyncio.sleep(5)
            print(f"Image generation task started for generation ID: {generation_id}")
        except Exception as err:
            async with session.begin():
                await session.refresh(generation)
                generation.status = Status.FAILED
                generation.error_message = str(err)
                raise err

        async with session.begin():
            await session.refresh(generation)
            generation.status = Status.COMPLETED
            generation.image_path = "s3://bucket/path/to/generated_image.png"
