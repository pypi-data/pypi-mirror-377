from dataclasses import dataclass, replace
from types import TracebackType
from typing import Optional, Self

from aiware.common.auth import AbstractTokenAuth
from aiware.graphql.async_client import AsyncAiwareGraphQL, AsyncAiwareGraphQLFactory
from aiware.search.async_client import AsyncAiwareSearch, AsyncAiwareSearchFactory

@dataclass
class AsyncAiware[G: AsyncAiwareGraphQL, S: AsyncAiwareSearch]:
    def __init__(
        self,
        *,
        graphql_endpoint: str,
        search_endpoint: str,
        graphql_factory: AsyncAiwareGraphQLFactory = lambda endpoint, auth: AsyncAiwareGraphQL(url=endpoint, auth=auth),
        search_factory: AsyncAiwareSearchFactory = lambda endpoint, auth: AsyncAiwareSearch(url=endpoint, auth=auth),
        auth: Optional[AbstractTokenAuth],
    ):
        self.auth: Optional[AbstractTokenAuth] = auth
        self.graphql_endpoint: str = graphql_endpoint
        self.search_endpoint: str = search_endpoint

        self.graphql_factory: AsyncAiwareGraphQLFactory[G] = graphql_factory
        self.search_factory: AsyncAiwareSearchFactory[S] = search_factory

        self.graphql: G = self.graphql_factory(endpoint=self.graphql_endpoint, auth=self.auth)
        self.search: S = self.search_factory(endpoint=self.search_endpoint, auth=self.auth)

    # @property
    # def auth(self) -> AbstractTokenAuth | None:
    #     return self._auth

    # @auth.setter
    # def auth(self, new_auth: AbstractTokenAuth | None):
    #     self._auth = new_auth
    #     self.graphql.auth = new_auth
    #     self.search.auth = new_auth

    async def __aenter__(self: Self) -> Self:
        await self.graphql.__aenter__()
        await self.search.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self.graphql.__aexit__(exc_type, exc_value, traceback)
        await self.search.__aexit__(exc_type, exc_value, traceback)

    def with_auth(self, auth: Optional[AbstractTokenAuth]) -> Self:
        copy = replace(self, auth=auth)
        copy.graphql = copy.graphql_factory(endpoint=self.graphql_endpoint, auth=auth)
        copy.search = copy.search_factory(endpoint=self.search_endpoint, auth=auth)

        return copy
