from typing import Dict, Any

from algernon import AlgObject, ajson
from algernon.aws.squirrel import SneakyKipper


class PaginationToken(AlgObject):
    def __init__(self,
                 username: str,
                 inclusive_start: int,
                 page_size: int,
                 pagination_id: str = None):
        if not pagination_id:
            import uuid
            pagination_id = uuid.uuid4().hex
        self._username = username
        self._inclusive_start = inclusive_start
        self._page_size = page_size
        self._pagination_id = pagination_id

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        return cls(
            json_dict['username'], json_dict['inclusive_start'],
            json_dict['page_size'], json_dict['pagination_id']
        )

    @classmethod
    def from_encrypted_token(cls, token, username):
        json_string = SneakyKipper('pagination').decrypt(token, {'username': username})
        obj_dict = ajson.loads(json_string)
        return cls(
            username, obj_dict['inclusive_start'],
            obj_dict['page_size'], obj_dict['pagination_id']
        )

    @property
    def to_gql(self):
        encrypted_value = self.package()
        return encrypted_value

    @property
    def inclusive_start(self):
        return self._inclusive_start

    @property
    def page_size(self):
        return self._page_size

    def increment(self) -> None:
        self._inclusive_start += self._page_size

    def package(self) -> str:
        unencrypted_text = ajson.dumps({
            'pagination_id': self._pagination_id,
            'inclusive_start': self._inclusive_start,
            'page_size': self._page_size
        })
        return SneakyKipper('pagination').encrypt(unencrypted_text, {'username': self._username})
