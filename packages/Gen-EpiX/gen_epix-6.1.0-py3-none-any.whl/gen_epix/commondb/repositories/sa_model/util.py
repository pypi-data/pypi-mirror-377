import importlib
from enum import Enum
from typing import Any, Callable, Type

import sqlalchemy as sa
from pydantic.fields import FieldInfo
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp import Domain, Entity
from gen_epix.fastapp.repositories import create_sa_type_from_field_info
from gen_epix.fastapp.repositories.sa.util import get_sa_type_kwargs_from_field_info


def create_table_args(
    model_class: Type[Model],
    field_name_map: dict[str, str] | None = None,
    **kwargs: Any,
) -> tuple:
    assert model_class.ENTITY is not None
    entity: Entity = model_class.ENTITY
    uq_constraints = []
    for field_names in entity.get_keys_field_names():
        sa_field_names = (
            [field_name_map.get(x, x) for x in field_names]
            if field_name_map
            else field_names
        )
        sa_field_name_str = "_".join(sa_field_names)
        uq_constraints.append(
            sa.UniqueConstraint(
                *sa_field_names,
                name=f"uq_{entity.table_name}_{sa_field_name_str}",
                **kwargs,
            )
        )
    if entity.schema_name:
        return entity.table_name, tuple(
            [*uq_constraints, {"schema": entity.schema_name}]
        )
    return entity.table_name, tuple([*uq_constraints])


def create_mapped_column(
    domain: Domain,
    model_class: Type[Model],
    field_name: str,
    field_name_map: dict[Type[Model], dict[str, str]] | None = None,
    **kwargs: Any,
) -> MappedColumn[Any]:
    assert model_class.ENTITY is not None
    entity: Entity = model_class.ENTITY
    field_info: FieldInfo = model_class.model_fields[field_name]
    sa_type = create_sa_type_from_field_info(field_info, field_info.annotation)
    nullable = kwargs.get("nullable", not field_info.is_required())
    doc = kwargs.pop("doc", field_info.description)
    link_entity = entity.get_link_entity(field_name)
    if link_entity and domain.get_service_type_for_entity(
        link_entity
    ) != domain.get_service_type_for_entity(entity):
        # Create foreign keys only within the same service
        link_entity = None
    ondelete = kwargs.pop("ondelete", None)
    onupdate = kwargs.pop("onupdate", None)
    if field_name_map is None:
        field_name_map = {}
    if model_class not in field_name_map:
        sa_field_name = field_name
    else:
        sa_field_name = field_name_map[model_class].get(field_name, field_name)
    fk_name = kwargs.pop("fk_name", f"fk_{entity.table_name}_{sa_field_name}")
    if link_entity:
        link_model_class = link_entity.model_class
        link_sa_id_field_name = (
            field_name_map[link_model_class][link_entity.id_field_name]
            if field_name_map
            else link_entity.id_field_name
        )
        ref_column_name = (
            f"{link_entity.schema_name}.{link_entity.table_name}.{link_sa_id_field_name}"
            if link_entity.schema_name
            else f"{link_entity.table_name}.{link_sa_id_field_name}"
        )
        return mapped_column(
            sa_type,
            sa.ForeignKey(
                ref_column_name, ondelete=ondelete, onupdate=onupdate, name=fk_name
            ),
            nullable=nullable,
            doc=doc,
            **kwargs,
        )
    return mapped_column(
        sa_type,
        nullable=nullable,
        primary_key=entity.id_field_name == field_name,
        doc=doc,
        **kwargs,
    )


def create_field_metadata(
    domain: Domain,
) -> tuple[
    dict[Type[Model], list[str]],
    dict[Type[Model], list[str]],
    dict[Type[Model], Callable[[Any, Any], dict[str, Any]]],
]:
    model_classes: frozenset[Type[Model]] = domain.models  # type: ignore[assignment]
    service_metadata_fields: dict[Type[Model], list[str]] = {
        model_class: ["_modified_by"] for model_class in model_classes
    }
    db_metadata_fields: dict[Type[Model], list[str]] = {
        model_class: [
            "_created_at",
            "_modified_at",
            "_version",
        ]
        for model_class in model_classes
    }
    generate_service_metadata: dict[
        Type[Model], Callable[[Any, Any], dict[str, Any]]
    ] = {
        model_class: lambda x, y: {
            "_modified_by": y,
        }
        for model_class in model_classes
    }
    return service_metadata_fields, db_metadata_fields, generate_service_metadata


def set_entity_repository_model_classes(
    domain: Domain,
    service_type_enum: Type[Enum],
    row_metadata_mixin_class: Type,
    service_modules_path: str,
    field_name_map: dict[Type, dict[str, str]] | None = None,
) -> None:
    if field_name_map is None:
        field_name_map = {}
    sa_metadata_field_names = set(row_metadata_mixin_class.__annotations__.keys()) - {
        "id"
    }
    sa_model_name_class_map = {}
    for service_type in service_type_enum:
        try:
            sa_module = importlib.import_module(
                f"{service_modules_path}.{service_type.value.lower()}"
            )
        except ModuleNotFoundError:
            continue
        for variable_content in sa_module.__dict__.values():
            if not hasattr(variable_content, "__tablename__"):
                # Not an SA model class
                continue
            sa_model_name_class_map[variable_content.__name__] = variable_content
    for entity in domain.get_dag_sorted_entities():
        if not entity.persistable:
            continue
        model_class = entity.model_class
        sa_model_class = sa_model_name_class_map.get(model_class.__name__)
        if not sa_model_class:
            raise ValueError(
                f"Model {model_class.__name__} does not have a corresponding SA model"
            )
        entity.set_db_model_class(sa_model_class)
        # Verify that the SA model has exactly the same fields as the model
        field_names = set(entity.get_field_names())
        relationship_field_names = set(entity.get_relationship_field_names())
        curr_field_name_map = field_name_map.get(model_class)
        if curr_field_name_map:
            field_names = {curr_field_name_map.get(x, x) for x in field_names}
        sa_field_names = (
            set(sa_model_class.__table__.columns.keys())
            - sa_metadata_field_names
            - relationship_field_names
        )
        extra_field_names = field_names - sa_field_names - relationship_field_names
        extra_field_names = {
            x for x in extra_field_names if f"{x}_id" not in field_names
        }
        if extra_field_names:
            extra_field_names_str = ", ".join(extra_field_names)
            raise ValueError(
                f"Model {model_class.__name__} has fields {extra_field_names_str} that are not in SA model {sa_model_class.__name__}"
            )
        extra_sa_field_names = sa_field_names - field_names
        if extra_sa_field_names:
            extra_field_names_str = ", ".join(extra_sa_field_names)
            raise ValueError(
                f"SA model {sa_model_class.__name__} has fields {extra_sa_field_names_str} that are not in model {model_class.__name__}"
            )


def get_mixin_mapped_column(
    model_mixin_class: Type,
    field_name: str,
    sa_column_type: Type[sa.types.TypeEngine],
    **kwargs: Any,
) -> Mapped:

    field_info: FieldInfo = getattr(model_mixin_class, field_name)
    annotation = model_mixin_class.__annotations__[field_name]
    # Extract SA arguments from mixin class based on sa_type
    kwargs["nullable"] = kwargs.get(  # pyright: ignore[reportArgumentType]
        "nullable", not field_info.is_required()
    )
    sa_column_type_kwargs = kwargs.pop(
        "sa_column_type_kwargs",
        get_sa_type_kwargs_from_field_info(sa_column_type, field_info),
    )
    # Create and return mapped column
    return mapped_column(
        create_sa_type_from_field_info(field_info, annotation, **sa_column_type_kwargs),
        **kwargs,
    )
