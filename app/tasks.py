import uuid
from typing import cast

import obstore as obs
import replicate
from replicate.helpers import FileOutput

from app.config import get_settings
from app.core.storage import store
from app.db.config import SessionLocal
from app.db.models import GenerationORM
from app.models import Status

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
        model_id = "black-forest-labs/flux-schnell"
        input = {"prompt": generation_orm.prompt}

        output = await replicate.async_run(model_id, input=input)
        output = cast(list[FileOutput], output)

        file_output = output[0]

        filename = f"{generation_orm.user_id}/outputs/{uuid.uuid4().hex}.{generation_orm.output_format}"
        await obs.put_async(store, filename, await file_output.aread())

        async with SessionLocal() as session:
            async with session.begin():
                generation_orm = await session.get(GenerationORM, generation_id)
                if not generation_orm:
                    raise ValueError(f"Generation with ID {generation_id} not found")
                generation_orm.status = Status.COMPLETED
                generation_orm.filename = filename
    except Exception as err:
        async with SessionLocal() as session:
            async with session.begin():
                generation_orm = await session.get(GenerationORM, generation_id)
                if not generation_orm:
                    raise ValueError(f"Generation with ID {generation_id} not found")
                generation_orm.status = Status.FAILED
                generation_orm.error_message = str(err)[1024:]
            raise err
