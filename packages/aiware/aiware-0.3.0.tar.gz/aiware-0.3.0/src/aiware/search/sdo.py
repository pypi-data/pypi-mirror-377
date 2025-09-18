from aiware.common.schemas import BaseSchema
from aiware.common.sdo import TypedSDO
from aiware.search.models import (
    SdoSliceSearchResult,
)
from aiware.search._models_generated import SearchResultsPage


from pydantic import Field


from typing import Annotated, Any, Dict, List, Optional, Type


class TypedSdoSliceSearchResult[T: BaseSchema](SearchResultsPage):
    results: List[TypedSDO[T]] = Field(default_factory=lambda: [])

    @staticmethod
    def from_sdo_search_result[S: BaseSchema](
        schema_cls: Type[S], schema_id: str, search_result: SdoSliceSearchResult
    ) -> "TypedSdoSliceSearchResult[S]":
        search_result_dict = search_result.model_dump(
            mode="python"
        )
        search_result_dict.pop("results", [])

        return TypedSdoSliceSearchResult.model_validate(
            {
                **search_result_dict,
                "results": [
                    TypedSDO.from_json(
                        schema_cls=schema_cls, schema_id=schema_id, json_data=result
                    )
                    for result in search_result.results or []
                ],
            }
        )
