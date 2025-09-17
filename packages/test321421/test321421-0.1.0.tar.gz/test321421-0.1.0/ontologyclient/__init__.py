
from typing import Set
from openapi_client import ApiClient, Configuration
from openapi_client.api.default_api import DefaultApi
from openapi_client.exceptions import ApiException

from .enum import EntityType


class OntologyClient():
    def __init__(self, endpoint: str="http://localhost:8000"):
        configuration = Configuration()
        configuration.host = endpoint

        # Create API client instance
        api_client = ApiClient(configuration)
        self.api = DefaultApi(api_client)

    async def get_children(self, et: EntityType) -> Set[EntityType]:
        res = self.api.get_children_get_children_get(node_id=et.value)
        return set([EntityType(child) for child in res])

if __name__ == "__main__":
    import asyncio

    async def main():
        client = OntologyClient()
        children = await client.get_children(EntityType.DISCHARGE_AIR_TEMPERATURE_SENSOR)
        print(children)

    asyncio.run(main())
