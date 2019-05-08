import logging
from typing import List, Dict, Tuple

from toll_booth.obj.graph.gql_scalars import InputVertex, InputEdge
from toll_booth.obj.graph.trident import TridentDriver

from toll_booth.obj.graph.generators import create_vertex_command_from_scalar, create_edge_command_from_scalar
from toll_booth.obj.graph.trident.trident_obj.pages import PaginationToken
from toll_booth.obj.graph.trident.trident_obj.edge import TridentEdge, TridentEdgeConnection


def _sort_edges(internal_id, unsorted_edges):
    edges = {
        'inbound': [],
        'outbound': [],
        'all': []
    }
    for edge in unsorted_edges:
        edge_type = 'inbound'
        if edge.in_id == internal_id:
            edge_type = 'outbound'
        edges[edge_type].append(edge)
        edges['all'].append(edge)
    return edges


class Ogm:
    def __init__(self, trident_driver=None):
        if not trident_driver:
            trident_driver = TridentDriver()
        self._trident_driver = trident_driver

    def query_vertex(self, internal_id: str):
        query = f"g.V('{internal_id}')"
        results = self._trident_driver.execute(query, read_only=True)
        for result in results:
            return result

    def query_vertex_properties(self, internal_id: str, property_names: List[str] = None):
        if not property_names:
            property_names = []
        filter_string = ','.join('"{0}"'.format(w) for w in property_names)
        query = f'g.V("{internal_id}").propertyMap([{filter_string}])'
        results = self._trident_driver.execute(query, read_only=True)
        logging.info(f'results from the query_vertex_properties query: {results}')
        if not results:
            return []
        return results

    def delete_vertex(self, internal_id: str):
        command = f"g.V('{internal_id}').drop()"
        return self._trident_driver.execute(command)

    def delete_edge(self, internal_id: str):
        command = f"g.E('{internal_id}').drop()"
        return self._trident_driver.execute(command)

    def graph_vertex(self, vertex_scalar: InputVertex):
        command = create_vertex_command_from_scalar(vertex_scalar)
        return self._trident_driver.execute(command)

    def graph_edge(self, edge_scalar: InputEdge):
        command = create_edge_command_from_scalar(edge_scalar)
        return self._trident_driver.execute(command)

    def get_edge_connection(self,
                            username: str,
                            context: Dict,
                            source: Dict,
                            token: str = None,
                            page_size: int = 10) -> TridentEdgeConnection:
        token_json = {
            'username': username,
            'token': token,
            'context': context,
            'source': source,
            'page_size': page_size
        }
        pagination_token = context.get('pagination_token', PaginationToken.from_json(token_json))
        internal_id = pagination_token.source.get('internal_id', pagination_token.context.get('internal_id'))
        edges, more = self._get_connected_edges(internal_id, pagination_token)
        pagination_token.increment()
        return TridentEdgeConnection(edges, pagination_token, more)

    def _get_connected_edges(self,
                             internal_id: str,
                             pagination_token: PaginationToken,
                             edge_labels: List[str] = None) -> Tuple[Dict[str, List[TridentEdge]], bool]:
        edge_filter = ', '.join([f"'{x}'" for x in edge_labels])
        inclusive_start = pagination_token.inclusive_start
        exclusive_end = pagination_token.exclusive_end
        query = f"g.V('{internal_id}').bothE({edge_filter}).range({inclusive_start}, {exclusive_end + 1})"
        edges = self._trident_driver.execute(query, read_only=True)
        returned_edges = edges[0:(exclusive_end - inclusive_start)]
        more = len(edges) > len(returned_edges)
        return _sort_edges(internal_id, returned_edges), more
