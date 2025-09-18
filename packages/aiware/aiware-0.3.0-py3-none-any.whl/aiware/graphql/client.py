from typing import Optional, Type, Union, Protocol
from aiware.common.auth import AbstractTokenAuth
from aiware.graphql.client_generated.client import GeneratedAiwareGraphQL

from aiware.common.schemas import BaseSchema
from aiware.common.sdo import TypedSDO
from aiware.graphql.sdo import TypedSDOPage
from aiware.graphql.client_generated.base_model_ref import UNSET, UnsetType
from aiware.graphql.utils import catch_not_found
from aiware.common.utils import not_none

class AiwareGraphQL(GeneratedAiwareGraphQL):
    def get_typed_sdo[S: BaseSchema](
        self, schema_cls: Type[S], schema_id: str, id: str
    ) -> Optional[TypedSDO[S]]:
        sdo_res = catch_not_found(
            lambda: self.get_sdo(id=id, schemaId=schema_id)
        )

        if sdo_res is None:
            return None

        return TypedSDO.from_json(
            schema_cls=schema_cls,
            schema_id=schema_id,
            json_data=not_none(sdo_res.structuredDataObject),
        )
    
    def get_typed_sdos[S: BaseSchema](
        self,
        schema_cls: Type[S],
        schema_id: str,
        limit: Union[Optional[int], UnsetType] = UNSET,
        offset: Union[Optional[int], UnsetType] = UNSET,
    ) -> TypedSDOPage[S]:
        sdos_res = self.get_sd_os(
            schemaId=schema_id, limit=limit, offset=offset
        )

        sdos_page = not_none(sdos_res.structuredDataObjects)

        return TypedSDOPage.from_sdo_page(schema_cls, sdos_page)

    def get_typed_sdos_by_ids[S: BaseSchema](
        self,
        schema_cls: Type[S],
        schema_id: str,
        ids: list[str],
    ) -> dict[str, TypedSDO[S]]:
        sdos: dict[str, TypedSDO[S]] = {}

        if len(ids) == 0:
            return sdos

        # FIXME: paginate

        sdos_res = self.get_sd_os(
            schemaId=schema_id, ids=ids, limit=len(ids)
        )

        sdos_page = not_none(sdos_res.structuredDataObjects)

        for sdo_ in not_none(sdos_page.records):
            sdo = not_none(sdo_)
            sdos[sdo.id] = TypedSDO.from_json(
                schema_cls, schema_id=schema_id, json_data=sdo
            )

        return sdos
    
    def create_typed_sdo[S: BaseSchema](
        self,
        schema_cls: Type[S],
        schema_id: str,
        id: str,
        sdo_data: S,
        *,
        exclude_unset: bool = False,
        exclude_none: bool = False
    ):
        create_res = self.create_sdo(
            schemaId=schema_id, id=id, data=sdo_data.dump_sdo(exclude_unset=exclude_unset, exclude_none=exclude_none)
        )

        return TypedSDO.from_json(
            schema_cls=schema_cls,
            schema_id=schema_id,
            json_data=not_none(create_res.createStructuredData),
        )

    def upsert_typed_sdo[S: BaseSchema](
        self, sdo: TypedSDO[S],
        *,
        exclude_unset: bool = False,
        exclude_none: bool = False
    ) -> TypedSDO[S]:
        self.update_sdo(
            schemaId=sdo.schemaId, id=sdo.id, data=sdo.data.dump_sdo(exclude_unset=exclude_unset, exclude_none=exclude_none)
        )

        return TypedSDO(
            schema_cls=sdo.schema_cls,
            schemaId=sdo.schemaId,
            id=sdo.id,
            createdDateTime=sdo.createdDateTime,
            modifiedDateTime=sdo.modifiedDateTime,
            data=sdo.data, # preserve reference
        )

class AiwareGraphQLFactory[G: AiwareGraphQL](Protocol):
    def __call__(self, endpoint: str, auth: Optional[AbstractTokenAuth]) -> G:
        ...
