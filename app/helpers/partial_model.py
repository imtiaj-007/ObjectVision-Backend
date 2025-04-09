from typing import (
    TypeVar,
    Type,
    Optional,
    get_origin,
    get_args,
    Union,
)
from pydantic import BaseModel, create_model, Field


T = TypeVar("T", bound=BaseModel)


def create_partial_model(
    model_cls: Type[T], name_suffix: str = "Patch"
) -> Type[BaseModel]:
    """
    Creates a new Pydantic model based on the input model where all fields are optional.
    Useful for PATCH operations in FastAPI.

    Args:
        model_cls: The original Pydantic model class
        name_suffix: Suffix to append to the original model name (default: "Patch")

    Returns:
        A new Pydantic model class with all fields made optional
    """
    fields = {}

    for field_name, field_info in model_cls.model_fields.items():
        field_type = field_info.annotation

        if get_origin(field_type) is Union and type(None) in get_args(field_type):
            fields[field_name] = (
                field_type,
                Field(
                    default=None,
                    **{
                        k: v
                        for k, v in (field_info.json_schema_extra or {}).items()
                        if k != "default_factory"
                    },
                ),
            )
            continue

        optional_type = Optional[field_type]
        
        fields[field_name] = (
            optional_type,
            Field(
                default=None,
                description=field_info.description,
                **{
                    k: v
                    for k, v in (field_info.json_schema_extra or {}).items()
                    if k != "default_factory"
                },
            ),
        )

    new_model_name = f"{model_cls.__name__}{name_suffix}"
    return create_model(new_model_name, **fields)
