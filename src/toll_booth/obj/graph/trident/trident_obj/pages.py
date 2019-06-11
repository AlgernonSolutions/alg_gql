from copy import deepcopy
from typing import Dict, Any

from algernon import AlgObject, ajson
from algernon.aws.squirrel import SneakyKipper


class PaginationToken(AlgObject):
    def __init__(self,
                 username: str,
                 source: Dict,
                 args: Dict,
                 inclusive_start: int = 0,
                 exclusive_end: int = 10,
                 pagination_id: str = None):
        if not pagination_id:
            import uuid
            pagination_id = uuid.uuid4().hex
        self._username = username
        self._source = source
        self._args = args
        self._inclusive_start = inclusive_start
        self._exclusive_end = exclusive_end
        self._pagination_id = pagination_id

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        try:
            return cls(
                json_dict['username'], json_dict['source'], json_dict['args'],
                json_dict['inclusive_start'], json_dict['exclusive_end'], json_dict['pagination_id']
            )
        except KeyError:
            token = json_dict['token']
            username = json_dict['username']
            source = json_dict['source']
            args = json_dict['args']
            if not token:
                return cls(username, source, args, exclusive_end=json_dict['page_size'])
            json_string = SneakyKipper('pagination').decrypt(token, {'username': username})
            obj_dict = ajson.loads(json_string)
            return cls(username, obj_dict['source'], obj_dict['args'], pagination_id=obj_dict['id'],
                       inclusive_start=obj_dict['start'], exclusive_end=obj_dict['end'])

    @property
    def to_gql(self):
        encrypted_value = self.package()
        return encrypted_value

    @property
    def source(self):
        return self._source

    @property
    def args(self):
        return self._args

    @property
    def inclusive_start(self):
        return self._inclusive_start

    @property
    def exclusive_end(self):
        return self._exclusive_end

    def increment(self) -> None:
        step_value = self._exclusive_end - self._inclusive_start
        self._inclusive_start += step_value
        self._exclusive_end += step_value

    def package(self) -> str:
        args = deepcopy(self._args)
        if 'token' in args:
            del(args['token'])
        unencrypted_text = ajson.dumps({
            'id': self._pagination_id,
            'source': self._source,
            'args': args,
            'start': self._inclusive_start,
            'end': self._exclusive_end
        })
        return SneakyKipper('pagination').encrypt(unencrypted_text, {'username': self._username})
