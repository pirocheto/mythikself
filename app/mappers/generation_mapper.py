from app.db.models import GenerationORM
from app.models import Generation


def orm_to_domain(user_orm: GenerationORM) -> Generation:
    return Generation(
        id=user_orm.id,
        user_id=user_orm.user_id,
        prompt=user_orm.prompt,
        created_at=user_orm.created_at,
        status=user_orm.status,
        output_format=user_orm.output_format,
        ratio=user_orm.ratio,
    )


def domain_to_orm(generation: Generation) -> GenerationORM:
    return GenerationORM(
        id=generation.id,
        user_id=generation.user_id,
        prompt=generation.prompt,
        created_at=generation.created_at,
        status=generation.status,
        output_format=generation.output_format,
        ratio=generation.ratio,
    )
