from typing import Dict, List, Any

from algernon import AlgObject

from toll_booth.obj.graph.trident.trident_obj.properties import TridentProperty
from toll_booth.obj.graph.trident.trident_obj import parse_object_properties


class TridentVertex(AlgObject):
    def __init__(self,
                 vertex_id: str,
                 vertex_label: str,
                 vertex_properties: Dict[str, List[TridentProperty]] = None):
        if not vertex_properties:
            vertex_properties = {}
        self._vertex_id = vertex_id
        self._vertex_label = vertex_label
        self._vertex_properties = vertex_properties

    def __len__(self):
        return 1

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        return cls(json_dict['vertex_id'], json_dict['vertex_label'], json_dict['vertex_properties'])

    @property
    def to_gql(self) -> Dict[str, Any]:
        gql = {
            'internal_id': self.vertex_id,
            'vertex_type': self.vertex_label,
            '__typename': 'Vertex'
        }
        gql_properties = []
        for property_name, vertex_properties in self._vertex_properties.items():
            property_value = parse_object_properties(property_name, vertex_properties)
            if property_name in ['id_value', 'identifier_stem']:
                gql[property_name] = property_value
                continue
            gql_properties.append(property_value)
        if gql_properties:
            gql['vertex_properties'] = gql_properties
        return gql

    @property
    def vertex_id(self) -> str:
        return self._vertex_id

    @property
    def vertex_label(self) -> str:
        return self._vertex_label

    @property
    def vertex_properties(self) -> Dict[str, List[TridentProperty]]:
        return self._vertex_properties

    def __iter__(self):
        return iter(self._vertex_properties)

    def __getitem__(self, item):
        return self._vertex_properties[item]

    def keys(self):
        return self._vertex_properties.keys()

    def values(self):
        return self._vertex_properties.values()

    def items(self):
        return self._vertex_properties.items()
