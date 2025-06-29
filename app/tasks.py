import uuid
from typing import cast

import obstore as obs
import replicate
from replicate.helpers import FileOutput

from app.config import get_settings
from app.core.storage import store
from app.db.config import SessionLocal
from app.db.models import GenerationORM, Status

settings = get_settings()

session = SessionLocal()


async def generate_image_task(generation_id: uuid.UUID) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            generation_orm = await session.get(GenerationORM, generation_id)
            if not generation_orm:
                raise ValueError(f"Generation with ID {generation_id} not found")
            generation_orm.status = Status.IN_PROGRESS

    try:
        # Run the image generation model using Replicate
        model_id = "black-forest-labs/flux-schnell"
        input = {"prompt": generation_orm.prompt}
        output = await replicate.async_run(model_id, input=input)
        output = cast(list[FileOutput], output)

        # Save the generated image to S3
        file_output = output[0]
        file_bytes = await file_output.aread()
        filename = f"{generation_orm.user_id}/outputs/{uuid.uuid4().hex}.{generation_orm.output_format}"
        await obs.put_async(store, filename, file_bytes)

        # Update the generation record in the database
        async with SessionLocal() as session:
            async with session.begin():
                generation_orm = await session.get(GenerationORM, generation_id)
                if not generation_orm:
                    raise ValueError(f"Generation with ID {generation_id} not found")
                generation_orm.status = Status.COMPLETED
                generation_orm.size = len(file_bytes)
                generation_orm.filename = filename
                generation_orm.content_type = f"image/{generation_orm.output_format.value}"

    except Exception as err:
        async with SessionLocal() as session:
            async with session.begin():
                generation_orm = await session.get(GenerationORM, generation_id)
                if not generation_orm:
                    raise ValueError(f"Generation with ID {generation_id} not found")
                generation_orm.status = Status.FAILED
                generation_orm.error_message = str(err)[1024:]
            raise err
