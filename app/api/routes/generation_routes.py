import uuid
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import get_settings
from app.db.models import GenerationORM
from app.mappers import generation_mapper
from app.models import Generation, OutputFormat, Ratio, Status, User
from app.schemas import GenerationCreateResponse, GenerationList, GenerationStatus
from app.tasks import generate_image_task

settings = get_settings()

router = APIRouter()


@router.post("/generations/create", status_code=status.HTTP_202_ACCEPTED, response_model=GenerationCreateResponse)
async def create_generation(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    prompt: Annotated[str, Form()],
    output_format: Annotated[OutputFormat, Form()] = OutputFormat.PNG,
    ratio: Annotated[Ratio, Form()] = Ratio.RATIO_1_1,
) -> Any:
    """Create a new generation request."""

    generation = Generation(
        prompt=prompt,
        user_id=current_user.id,
        output_format=output_format,
        ratio=ratio,
        status=Status.PENDING,
    )

    generation_orm = generation_mapper.domain_to_orm(generation)
    async with session.begin():
        session.add(generation_orm)

        # Trigger the background task to generate the image
        background_tasks.add_task(generate_image_task, generation_id=generation_orm.id)

    return GenerationCreateResponse(
        message="Generation request created successfully",
        generation_id=generation.id,
    )


@router.get("/generations", response_model=GenerationList)
async def get_generations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Retrieve all generations for the current user."""

    # Get the count of generations for the current user
    count_statement = select(func.count()).select_from(GenerationORM).where(GenerationORM.user_id == current_user.id)
    count_result = await session.execute(count_statement)
    count = count_result.scalars().one()

    # Get the list of generations for the current user
    select_statement = select(GenerationORM).where(GenerationORM.user_id == current_user.id)
    result = await session.execute(select_statement)
    generations_orm = result.scalars().all()
    generations = [generation_mapper.orm_to_domain(gen) for gen in generations_orm]

    return {"count": count, "data": generations}


@router.get("/generations/{generation_id}", response_model=Generation)
async def get_generation(
    generation_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Retrieve a specific generation by ID."""

    statement = select(GenerationORM).where(
        GenerationORM.id == generation_id,
        GenerationORM.user_id == current_user.id,
    )
    result = await session.execute(statement)
    generation_orm = result.scalars().one_or_none()

    if not generation_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")

    return generation_mapper.orm_to_domain(generation_orm)


@router.get("/generations/{generation_id}/status", response_model=GenerationStatus)
async def get_generation_status(
    generation_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Retrieve the status of a specific generation by ID."""

    statement = select(GenerationORM).where(
        GenerationORM.id == generation_id,
        GenerationORM.user_id == current_user.id,
    )
    result = await session.execute(statement)
    generation_orm = result.scalar_one_or_none()

    if generation_orm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")

    return generation_mapper.orm_to_domain(generation_orm)


@router.delete("/generations/{generation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generation(
    generation_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a specific generation by ID."""

    async with session.begin():
        statement = select(GenerationORM).where(
            GenerationORM.id == generation_id,
            GenerationORM.user_id == current_user.id,
        )
        result = await session.execute(statement)
        generation_orm = result.scalars().one_or_none()

        if not generation_orm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")

        await session.delete(generation_orm)
