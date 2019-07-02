from typing import List, Dict, Any

from algernon import AlgObject

from toll_booth.obj.graph.trident.trident_obj.edge import TridentEdge
from toll_booth.obj.graph.trident.trident_obj.pages import PaginationToken


class PageInfo(AlgObject):
    def __init__(self, next_token: PaginationToken, more: bool):
        self._next_token = next_token
        self._more = more

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['next_token'], json_dict['more'])

    @property
    def to_gql(self):
        return {
            "__typename": 'PageInfo',
            'next_token': self._next_token,
            'more': self._more
        }


class ConnectedEdge(AlgObject):
    def __init__(self,
                 internal_id: str,
                 edge_label: str,
                 vertex: str):
        self._internal_id = internal_id
        self._edge_label = edge_label
        self._vertex = vertex

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['internal_id'], json_dict['edge_label'], json_dict['vertex'])

    @classmethod
    def from_raw_edge(cls, raw_edge: TridentEdge, source_internal_id: str):
        edge_label = raw_edge.label
        internal_id = raw_edge.internal_id
        if raw_edge.in_id == source_internal_id:
            return cls(internal_id, edge_label, raw_edge.out_id)
        return cls(internal_id, edge_label, raw_edge.in_id)

    @property
    def internal_id(self):
        return self._internal_id

    @property
    def edge_label(self):
        return self._edge_label

    @property
    def vertex(self):
        return self._vertex

    @property
    def to_gql(self) -> Dict[str, Any]:
        return {
            '__typename': 'ConnectedEdge',
            'internal_id': self._internal_id,
            'edge_label': self._edge_label,
            'vertex': {
                '__typename': 'Vertex',
                'internal_id': self._vertex
            }
        }


class ConnectedEdgePage(AlgObject):
    def __init__(self, edges: List[ConnectedEdge], page_info: PageInfo):
        self._edges = edges
        self._page_info = page_info

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['edges'], json_dict['page_info'])

    @property
    def to_gql(self):
        return {
            '__typename': 'ConnectedEdgePage',
            'edges': self._edges,
            'page_info': self._page_info
        }


class EdgeConnection(AlgObject):
    def __init__(self,
                 edge_label: str,
                 edges: List[ConnectedEdge] = None,
                 total_count: int = None,
                 page_info: PageInfo = None):
        self._edge_label = edge_label
        self._edges = edges
        self._total_count = total_count
        self._page_info = page_info

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        return cls(json_dict['edges'], json_dict['total_count'], json_dict.get('page_info'))

    @property
    def to_gql(self) -> Dict[str, Any]:
        gql = {
            '__typename': 'EdgeConnection',
            'edge_label': self._edge_label
        }
        if self._total_count:
            gql['total_count'] = self._total_count
        if self._page_info:
            gql['page_info'] = self._page_info
        if self._edges:
            gql['edges'] = self._edges
        return gql
