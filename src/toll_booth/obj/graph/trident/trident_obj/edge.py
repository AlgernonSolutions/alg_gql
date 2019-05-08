from typing import Dict, List, Any

from algernon import AlgObject

from toll_booth.obj.graph.trident.trident_obj import parse_object_properties
from toll_booth.obj.graph.trident.trident_obj.pages import PaginationToken
from toll_booth.obj.graph.trident.trident_obj.properties import TridentProperty
from toll_booth.obj.graph.trident.trident_obj.vertex import TridentVertex


class TridentEdge(AlgObject):
    def __init__(self,
                 internal_id: str,
                 label: str,
                 from_vertex: TridentVertex,
                 to_vertex: TridentVertex,
                 edge_properties: Dict[str, List[TridentProperty]] = None):
        if not edge_properties:
            edge_properties = {}
        self._internal_id = internal_id
        self._label = label
        self._from_vertex = from_vertex
        self._to_vertex = to_vertex
        self._edge_properties = edge_properties

    def __len__(self):
        return 1

    @classmethod
    def parse_json(cls, json_dict):
        return cls(
            json_dict['internal_id'], json_dict['label'],
            json_dict['from_vertex'], json_dict['to_vertex'],
        )

    @property
    def to_gql(self):
        gql = {
            'internal_id': self.internal_id,
            'edge_label': self.label,
            'from_vertex': self._from_vertex,
            'to_vertex': self._to_vertex,
            '__typename': 'Edge'
        }
        gql_properties = []
        for property_name, edge_properties in self._edge_properties.items():
            property_value = parse_object_properties(property_name, edge_properties)
            if property_name in ['id_value', 'identifier_stem']:
                gql[property_name] = property_value
            gql_properties.append({'property_name': property_name, 'property_value': property_value})
        if gql_properties:
            gql['edge_properties'] = gql_properties
        return gql

    @property
    def internal_id(self):
        return self._internal_id

    @property
    def label(self):
        return self._label

    @property
    def in_id(self):
        return self._from_vertex.vertex_id

    @property
    def out_id(self):
        return self._to_vertex.vertex_id


class TridentPageInfo(AlgObject):
    def __init__(self, token: PaginationToken, more: bool):
        self._token = token
        self._more = more

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['token'], json_dict['more'])

    @property
    def to_gql(self):
        return {
            'token': self._token,
            'more': self._more,
            '__typename': 'PageInfo'
        }


class TridentEdgeConnection(AlgObject):
    def __init__(self,
                 edges: Dict[str, List[TridentEdge]],
                 token: PaginationToken,
                 more: bool,
                 page_info: TridentPageInfo = None):
        if not page_info:
            page_info = TridentPageInfo(token, more)
        self._edges = edges
        self._token = token
        self._more = more
        self._page_info = page_info

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        return cls(json_dict['edges'], json_dict['token'], json_dict['more'], json_dict.get('page_info'))

    @property
    def page_info(self) -> TridentPageInfo:
        return self._page_info

    @property
    def in_count(self) -> int:
        return len(self._edges['inbound'])

    @property
    def out_count(self) -> int:
        return len(self._edges['outbound'])

    @property
    def total_count(self) -> int:
        return len(self._edges['all'])

    @property
    def to_gql(self) -> Dict[str, Any]:
        return {
            '__typename': 'EdgeConnection',
            'edges': self._edges,
            'page_info': self._page_info,
            'total_count': self.total_count,
            'in_count': self.in_count,
            'out_count': self.out_count
        }
