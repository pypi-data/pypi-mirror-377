from typing import Annotated, Any, Dict, List, Optional, Self, Type, cast, Protocol
import httpx
from pydantic import Field
from aiware.common.auth import AbstractTokenAuth
from aiware.common.schemas import BaseSchema
from aiware.search.models import (
    SdoSliceSearchResult,
    SearchRequestFilter,
    SearchSDOsRequest,
    VectorSearchRequest,
    SearchRequest,
    SliceSearchResult,
    VectorSearchResults,
)
from aiware.search.sdo import TypedSdoSliceSearchResult

class AiwareSearch:
    def __init__(
        self,
        url: str = "",
        auth: Optional[AbstractTokenAuth] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.url = url
        self.auth = auth
        self.headers = headers
        self.http_client = http_client if http_client else httpx.Client(base_url=url, headers=headers, auth=auth)

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        self.http_client.close()

    def search_media(self, request: SearchRequest) -> SliceSearchResult:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = self.http_client.post("/", json=data)
        response.raise_for_status()

        return SliceSearchResult.model_validate_json(response.text)

    def search_sdos(self, request: SearchSDOsRequest) -> SdoSliceSearchResult:
        return (self.search_media(request=cast(SearchRequest, request))).as_model(SdoSliceSearchResult)

    def vector_search(self, request: VectorSearchRequest) -> VectorSearchResults:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = self.http_client.post("/vector", json=data)
        response.raise_for_status()

        return VectorSearchResults.model_validate_json(response.text)
    
    def search_typed_sdos[S: BaseSchema](
        self,
        schema_cls: Type[S],
        schema_id: str,
        query: SearchRequestFilter,
        sort: Annotated[
            Optional[List[Dict[str, Any]]],
            Field(
                description="See https://github.com/veritone/core-search-server#sort-statements."
            ),
        ] = None,
        offset: Annotated[
            Optional[float],
            Field(
                description="Used for paging, indicates the zero-base index of the first result. If not provided, defaults to 0."
            ),
        ] = None,
        limit: Annotated[
            Optional[float],
            Field(
                description="Maximum of results to return. Cannot exceed 100. Defaults to 10."
            ),
        ] = None,
    ) -> TypedSdoSliceSearchResult[S]:
        untyped_search_result = self.search_sdos(
            SearchSDOsRequest(
                index=["mine"],
                type=schema_id,
                query=query,
                sort=sort,
                offset=offset,
                limit=limit,
            )
        )

        return TypedSdoSliceSearchResult.from_sdo_search_result(
            schema_cls=schema_cls,
            schema_id=schema_id,
            search_result=untyped_search_result,
        )

class AiwareSearchFactory[S: AiwareSearch](Protocol):
    def __call__(self, endpoint: str, auth: Optional[AbstractTokenAuth]) -> S:
        ...
