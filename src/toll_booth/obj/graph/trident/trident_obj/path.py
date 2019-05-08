from typing import List, Union

from algernon import AlgObject

from toll_booth.obj.graph.trident.trident_obj.edge import TridentEdge
from toll_booth.obj.graph.trident.trident_obj.vertex import TridentVertex

GraphObjects = Union[TridentVertex, TridentEdge]


class TridentPath(AlgObject):
    def __init__(self, labels: List[str], path_objects: [GraphObjects]):
        self._labels = labels
        self._path_objects = path_objects

    @classmethod
    def parse_json(cls, json_dict):
        return cls(
            json_dict['labels'],
            json_dict['path_objects']
        )

    @property
    def labels(self):
        return self._labels

    @property
    def path_objects(self):
        return self._path_objects
