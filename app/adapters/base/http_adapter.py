import json
import logging
from json import JSONDecodeError

import aiohttp
from aiohttp import ClientResponse
from aiohttp.client_reqrep import ClientResponse

from app.adapters.errors import ClientError


class BaseAiohttpClient:  # pragma: no cover

    async def make_request(
        self, method, url, raw_response: bool = False, **kwargs
    ) -> ClientResponse:
        async with aiohttp.request(method, url, **kwargs) as response:
            await response.read()
            return (
                response if raw_response else await self.parse_response(response, url)
            )

    async def parse_response(self, response: ClientResponse, url: str) -> str:
        return await response.text()


class AiohttpJSONClient(BaseAiohttpClient):

    async def parse_response(self, response: ClientResponse, url: str) -> dict:
        """Вернуть ответ в виде словаря.

        Args:
            response (ClientResponse): ответ от сервера
            url (str): url

        Returns:
            dict: распаршенный json ответ от сервера
        """
        response_text = await response.text()
        try:
            json_answer = json.loads(response_text)
        except JSONDecodeError as err:
            msg = f"Invalid answer from {url}: {response_text}. {err}"
            logging.error(msg)
            raise ClientError(msg) from None
        else:
            return json_answer
