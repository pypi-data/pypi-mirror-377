import logging
import pathlib
from operator import itemgetter
from typing import Any, Dict, List, Type, Union, Tuple

from alembic import command
from alembic.config import Config
from hmd_meta_types import Entity, Noun, Relationship
from sqlalchemy import MetaData, create_engine, insert, update
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import and_, or_, select

from hmd_cli_tools import cd
from hmd_schema_loader import DefaultLoader
from .base_engine import BaseEngine, gen_new_key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SqliteEngine(BaseEngine):
    def __init__(self, database_path: Union[str, pathlib.Path], echo=False):
        self._db_uri = f"sqlite+pysqlite:///{database_path}"
        logger.info(self._db_uri)
        lib_dir = pathlib.Path(__file__).absolute().parent.parent

        alembic_dir = lib_dir / "alembic"
        alembic_ini = alembic_dir / "alembic.ini"

        if alembic_ini.exists():
            logger.info(alembic_ini)

            with cd(alembic_dir):
                alembic_cfg = Config()
                alembic_cfg.set_main_option("script_location", ".")
                alembic_cfg.set_main_option("sqlalchemy.url", self._db_uri)
                command.upgrade(alembic_cfg, "head")
        self._engine = create_engine(self._db_uri, echo=echo, future=True)

        self._metadata = MetaData()
        self._metadata.reflect(bind=self._engine)
        self.tables = {
            Noun: self._metadata.tables["entity"],
            Relationship: self._metadata.tables["relationship"],
        }

    def _deserialze_entity(self, entity_def, row):
        if issubclass(entity_def, Relationship):
            identifier, content, rel_from, rel_to = row
            return Entity.deserialize(
                entity_def,
                {
                    **{
                        "identifier": identifier,
                        "ref_from": rel_from,
                        "ref_to": rel_to,
                    },
                    **content,
                },
            )

        identifier, content = row
        data = {"identifier": identifier, **content}
        return Entity.deserialize(entity_def, data)

    def _deserialze_entities(self, entity_def, rows):
        return [self._deserialze_entity(entity_def, row) for row in rows]

    def get_entity(self, entity_def: Type[Entity], id: str) -> Entity:
        if issubclass(entity_def, Noun):
            return self.get_noun(entity_def, id)
        else:
            raise NotImplementedError()

    def get_entities(self, entity_def: Type[Entity], ids_: List[str]) -> List[Entity]:
        # todo: attempt to query multiple entities at the same time
        if not issubclass(entity_def, Noun):
            raise NotImplementedError()

        results = []
        for id_ in ids_:
            result = self.get_noun(entity_def, id_)
            if not result:
                raise Exception(
                    f"Entity of type {entity_def.get_namespace_name()} with id {id_} not found."
                )
            results.append(result)
        return results

    def get_noun(self, entity_def: Type[Noun], id: str) -> Noun:
        def_name = entity_def.get_namespace_name()
        columns = self.tables[Noun].columns
        query = select(columns.id, columns.content).where(
            columns.id == id, columns.name == def_name, columns.is_deleted == False
        )

        with Session(self._engine) as session:
            result = session.execute(query).fetchone()
            if result:
                return self._deserialze_entity(entity_def, result)
        return None

    def search_entities(
        self, entity_def: Type[Entity], search_filter: Dict[str, Any] = dict()
    ) -> List[Entity]:
        if issubclass(entity_def, Noun):
            return self.search_noun(entity_def, search_filter)
        elif issubclass(entity_def, Relationship):
            return self.search_relationships(entity_def, search_filter)
        else:
            raise NotImplementedError()

    def build_where_clause(self, table, condition: Dict[str, Any]):
        if "and" in condition:
            subs = [
                self.build_where_clause(table, sub_condition)
                for sub_condition in condition["and"]
            ]
            return and_(*subs)

        elif "or" in condition:
            subs = [
                self.build_where_clause(table, sub_condition)
                for sub_condition in condition["or"]
            ]
            return or_(*subs)
        else:
            attribute, operator_key = itemgetter("attribute", "operator")(condition)
            where_sql = table.c.content[attribute].as_string().op(operator_key)
            if "value" in condition:
                where_sql = where_sql(condition["value"])
            elif "attribute_target" in condition:
                where_sql = where_sql(
                    table.c.content[condition["attribute_target"]].as_string()
                )

            return where_sql

    def search_noun(
        self, entity_def: Type[Noun], search_filter: Dict[str, Any] = dict()
    ) -> List[Noun]:
        self._validate_search_criteria(entity_def.entity_definition(), search_filter)
        table = self.tables[Noun]
        if len(search_filter) > 0:
            query = select(table.c.id, table.c.content).where(
                table.c.name == entity_def.get_namespace_name(),
                self.build_where_clause(table, search_filter),
            )
            with Session(self._engine) as session:
                results = session.execute(query).fetchall()
                if len(results) > 0:
                    return self._deserialze_entities(entity_def, results)

        return []

    def search_relationships(
        self, entity_def: Type[Relationship], search_filter: Dict[str, Any]
    ) -> List[Relationship]:
        raise NotImplementedError()

    def list_entities(self, loader: DefaultLoader, id: str = None) -> List[Noun]:
        columns = self.tables[Noun].columns
        query = select(columns.id, columns.name, columns.content).where(
            columns.is_deleted == False
        )

        if id is not None:
            query = query.where(columns.id == id)

        ret = []
        with Session(self._engine) as session:
            results = session.execute(query).fetchall()

            if len(results) > 0:
                for row in results:
                    entity_class = loader.get(row["name"])
                    if entity_class is None:
                        raise Exception(f"No entity type found for name {row['name']}")
                    ret.append(entity_class(identifier=row["id"], **row["content"]))

        return ret

    def put_entity(self, entity: Type[Entity]):
        if isinstance(entity, Noun):
            return self.put_noun(entity)
        else:
            return self.put_relationship(entity)

    def get_upsert_statement(self, entity: Entity):
        table = self.tables[Relationship]
        if isinstance(entity, Noun):
            table = self.tables[Noun]

        if entity.identifier is None:
            return insert(table)
        return update(table).where(table.c.id == entity.identifier)

    def put_noun(self, entity: Noun) -> Noun:
        statement = self.get_upsert_statement(entity)
        if not hasattr(entity, "identifier") or entity.identifier is None:
            entity.identifier = gen_new_key()

        with Session(self._engine) as session:
            entity_dict = entity.serialize()
            if "identifier" in entity_dict:
                del entity_dict["identifier"]
            session.execute(
                statement,
                {
                    "id": entity.identifier,
                    "name": entity.__class__.get_namespace_name(),
                    "content": entity_dict,
                },
            )
            session.commit()
        return entity

    def put_relationship(self, relationship: Relationship) -> Relationship:
        statement = self.get_upsert_statement(relationship)
        if not hasattr(relationship, "identifier") or relationship.identifier is None:
            relationship.identifier = gen_new_key()
        with Session(self._engine) as session:
            rel_dict = relationship.serialize()
            if "identifier" in rel_dict:
                del rel_dict["identifier"]
            del rel_dict["ref_from"]
            del rel_dict["ref_to"]
            from_id = (
                relationship.ref_from
                if isinstance(relationship.ref_from, str)
                else relationship.ref_from.identifier
            )
            to_id = (
                relationship.ref_to
                if isinstance(relationship.ref_to, str)
                else relationship.ref_to.identifier
            )
            session.execute(
                statement,
                {
                    "id": relationship.identifier,
                    "name": relationship.__class__.get_namespace_name(),
                    "content": rel_dict,
                    "from_name": relationship.ref_from_type().get_namespace_name(),
                    "from_id": from_id,
                    "to_name": relationship.ref_to_type().get_namespace_name(),
                    "to_id": to_id,
                },
            )
            session.commit()
        return relationship

    def delete_entity(self, entity_def: Type[Entity], id) -> None:
        with Session(self._engine) as session:
            table = self.tables[Relationship]
            if issubclass(entity_def, Noun):
                statement = (
                    update(table)
                    .where(or_(table.c.from_id == id, table.c.to_id == id))
                    .values(is_deleted=True)
                )

                session.execute(statement)
                table = self.tables[Noun]

            statement = (
                update(table)
                .where(
                    and_(
                        table.c.id == id,
                        table.c.name == entity_def.get_namespace_name(),
                    )
                )
                .values(is_deleted=True)
            )
            session.execute(statement)

            session.commit()

    def _get_relationships(
        self, relationship_def: Type[Relationship], id, from_to: str
    ) -> List[Relationship]:
        if from_to not in ["from", "to"]:
            raise Exception(f'argument, from_to, must be "from" or "to", was {from_to}')
        results = []
        with Session(self._engine) as session:
            columns = self.tables[Relationship].columns
            noun_from = aliased(self.tables[Noun])
            noun_to = aliased(self.tables[Noun])
            query = (
                session.query(columns.id, columns.content, noun_from.c.id, noun_to.c.id)
                .join(
                    noun_from,
                    and_(
                        noun_from.c.id == columns.from_id,
                        noun_from.c.name == columns.from_name,
                    ),
                )
                .join(
                    noun_to,
                    and_(
                        noun_to.c.id == columns.to_id, noun_to.c.name == columns.to_name
                    ),
                )
                .filter(
                    and_(
                        columns[f"{from_to}_id"] == id,
                        columns.name == relationship_def.get_namespace_name(),
                        columns.is_deleted == False,
                    )
                )
            )
            data = session.execute(query).fetchall()
            if len(data) > 0:
                for row in data:
                    rel_id, rel_content, from_id, to_id = row
                    rel = Entity.deserialize(
                        relationship_def,
                        {
                            **{
                                "identifier": rel_id,
                                "ref_from": from_id,
                                "ref_to": to_id,
                            },
                            **rel_content,
                        },
                    )
                    results.append(rel)
                # return self._deserialze_entities(relationship_def, results)

        return results

    def get_relationships_from(
        self, relationship_def: Relationship, id: int
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id, "from")

    def get_relationships_to(
        self, relationship_def: Relationship, id: int
    ) -> List[Relationship]:
        return self._get_relationships(relationship_def, id, "to")

    def upsert_entities(self, entities):
        return NotImplementedError()

    def native_query_nouns(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def native_query_relationships(
        self, query: Any, data: Dict[str, Any]
    ) -> List[Tuple[str, Dict]]:
        raise NotImplementedError()

    def begin_transaction(self) -> None:
        pass

    def commit_transaction(self) -> None:
        pass

    def rollback_transaction(self) -> None:
        pass
