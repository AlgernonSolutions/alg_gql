import logging
from typing import Dict, Any

from toll_booth.obj.graph.ogm import Ogm

known_fields = ('edges',)


def handler(type_name: str,
            field_name: str,
            args: Dict[str, Any],
            source: Dict[str, Any],
            result: Dict[str, Any],
            request: Dict[str, Any],
            identity: Dict[str, Any]) -> Any:
    if type_name == 'EdgeConnection':
        ogm = Ogm()
        if field_name == 'edges':
            logging.info('request resolved to EdgeConnection.edges')
            if identity in ('None', None):
                identity = {}
                logging.warning(f'processed request for EdgeConnection.edges, no identity provided,'
                                f'this is ok for development, but should not occur in production')
            username = identity.get('username')
            if not username:
                username = request['headers']['x-api-key']
            internal_id = source.get('source_internal_id')
            edge_label = source.get('edge_label')
            page_size = args.get('page_size')
            next_token = args.get('after')
            connected_edges = ogm.get_connected_edge_page(username, internal_id, edge_label, page_size, next_token)
            return connected_edges
