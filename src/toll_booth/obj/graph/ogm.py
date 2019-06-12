import logging
from typing import List, Dict, Any

from toll_booth.obj.graph.generators import create_vertex_command_from_scalar, create_edge_command_from_scalar
from toll_booth.obj.graph.gql_scalars.connected_edges import PageInfo, ConnectedEdge, ConnectedEdgePage
from toll_booth.obj.graph.gql_scalars.inputs import InputVertex, InputEdge
from toll_booth.obj.graph.trident import TridentDriver
from toll_booth.obj.graph.trident.trident_obj.pages import PaginationToken


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

    def get_connected_edge_page(self,
                                username: str,
                                internal_id: str,
                                edge_label: str,
                                page_size: int,
                                next_token: str = None) -> ConnectedEdgePage:
        pagination_token = PaginationToken(username, 0, page_size)
        if next_token:
            pagination_token = PaginationToken.from_encrypted_token(next_token, username)
        inclusive_start = pagination_token.inclusive_start
        exclusive_end = inclusive_start + page_size
        query = f"g.V('{internal_id}').bothE().hasLabel('{edge_label}').range({inclusive_start}, {exclusive_end + 1})"
        queried_edges = self._trident_driver.execute(query, read_only=True)
        edges = queried_edges[::len(queried_edges) - 1]
        more = len(queried_edges) > len(edges)
        pagination_token.increment()
        connected_edges = [ConnectedEdge.from_raw_edge(x, internal_id) for x in edges]
        page_info = PageInfo(pagination_token, more)
        return ConnectedEdgePage(connected_edges, page_info)

    def query_edge_connections(self,
                               internal_id: str,
                               edge_labels: List[str] = None) -> List[Dict[str, Any]]:
        filter_statement = ''
        if edge_labels:
            edge_filter = ', '.join([f"'{x}'" for x in edge_labels])
            filter_statement = f'.hasLabel({edge_filter})'
        query = f"g.V('{internal_id}').bothE(){filter_statement}.group().by(label).by(count())"
        results = self._trident_driver.execute(query, read_only=True)
        for result in results:
            return [{'edge_label': x, 'total_count': y, '__typename': 'EdgeConnection'} for x, y in result.items()]
