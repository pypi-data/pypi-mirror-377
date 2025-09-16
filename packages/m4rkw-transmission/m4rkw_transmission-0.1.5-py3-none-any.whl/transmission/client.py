import re
import time
from typing import Any, List, Optional, Union, cast

import sys
import requests

from transmission import (
    ATTRIBUTES_ALL,
    ATTRIBUTES_LIST,
    ATTRIBUTES_MUTABLE,
    ATTRIBUTES_SESSION,
    ATTRIBUTES_SESSION_MUTABLE,
    RPC_METHODS,
    Torrent,
    TransmissionResponse,
    TransmissionResponseStatus,
)


class Transmission:

    def __init__(self, host: str, port: int, user: str, password: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password


    def rpc(self, method: str, args: dict[str, str | int | List[str] | List[int]] = {}, session_id: Optional[str] = None) -> TransmissionResponse:
        resp = requests.post(f'http://{self.host}:{self.port}/transmission/rpc', json={
                'method': method,
                'arguments': args
            }, headers={
                'X-Transmission-Session-Id': session_id,
                'Content-type': 'application/json'
            }, auth=(self.user, self.password))

        if resp.status_code == 409:
            match = re.match('^.*?X-Transmission-Session-Id: (.*?)<', resp.text)
            return self.rpc(method, args, match.group(1) if match else '')

        response = TransmissionResponse(**resp.json())

        if response.result != "success":
            raise Exception("RPC error: " + response.result)

        return response


    def get(self, id: int, attributes: List[str] = ATTRIBUTES_ALL) -> Torrent | bool:
        for attr in attributes:
            if attr not in ATTRIBUTES_ALL:
                raise Exception("Unknown torrent attributes: %s" % (attr))

        if len(attributes) == 0:
            attributes = ATTRIBUTES_ALL

        params: dict[str, str | int | List[str] | List[int]] = {
            'fields': attributes,
            'ids': [id]
        }

        resp = self.rpc('torrent-get', params)

        if resp.arguments.torrents is None:
            return False

        if len(resp.arguments.torrents) > 0:
            return resp.arguments.torrents[0]

        return False


    def list(self, attributes: List[str] = ATTRIBUTES_LIST) -> list[Torrent]:
        for attr in attributes:
            if attr not in ATTRIBUTES_ALL:
                raise Exception("Unknown torrent attributes: %s" % (attr))

        if len(attributes) == 0:
            attributes = ATTRIBUTES_ALL

        params: dict[str, str | int | List[str] | List[int]] = {
            'fields': attributes
        }

        resp = self.rpc('torrent-get', params)

        if resp is None:
            return []

        return cast(list[Torrent], resp.arguments.torrents)


    def get_attr(self, id: int, attribute: str) -> Any:
        resp = self.get(id, [attribute])

        if type(resp) is bool:
            raise Exception(f"Torrent with id {id} not found.")

        return getattr(resp, attribute)


    def set_attr(self, id: int, attribute: str, value: Any) -> bool:
        resp = self.rpc('torrent-set', {'ids': [id], attribute: value})
        return resp.result == TransmissionResponseStatus.SUCCESS


    def add(self, params: dict[str, Any] = {}) -> int:
        resp = self.rpc('torrent-add', params)

        if resp.arguments.torrent_added is None:
            raise Exception(f"failed to add torrent: {resp}")

        return resp.arguments.torrent_added.id


    def add_magnet(self, magnet_link: str, params: dict[str, Any] = {}) -> int:
        if magnet_link[0:8] != 'magnet:?':
            raise Exception("This doesn't look like a magnet link to me: %s" % (magnet_link))

        arg: dict[str, Any] = {'filename': magnet_link}

        resp = self.rpc('torrent-add', arg)

        if resp.arguments.torrent_added is None:
            raise Exception(f"failed to add torrent: {resp}")

        return resp.arguments.torrent_added.id


    def delete(self, id: int, delete_local_data: bool = True) -> bool:
        resp = self.rpc('torrent-remove',{
            'ids': [id],
            'delete-local-data': delete_local_data
        })

        return resp.result == TransmissionResponseStatus.SUCCESS


    def start(self, id: int) -> bool:
        resp = self.rpc('torrent-start',{
            'ids': [id]
        })

        return resp.result == TransmissionResponseStatus.SUCCESS


    def stop(self, id: int) -> bool:
        resp = self.rpc('torrent-stop',{
            'ids': [id]
        })

        return resp.result == TransmissionResponseStatus.SUCCESS
