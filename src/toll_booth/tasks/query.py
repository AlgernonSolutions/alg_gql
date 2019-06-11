import logging
from typing import Dict, Any

from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.troubles import InvalidGqlRequestException

known_fields = ('edges')


def handler(type_name: str,
            field_name: str,
            args: Dict[str, Any],
            source: Dict[str, Any],
            result: Dict[str, Any],
            request: Dict[str, Any],
            identity: Dict[str, Any]) -> Any:
    if type_name == 'Query':
        ogm = Ogm()
        if field_name == 'edges':
            logging.info('request resolved to Query.edges')
            internal_id = args.get('internal_id')
            if internal_id is None:
                raise InvalidGqlRequestException(type_name, field_name, ['internal_id'])
            if identity in ('None', None):
                identity = {}
                logging.warning(f'processed request for Vertex.connected_edges, no identity provided,'
                                f'this is ok for development, but should not occur in production')
            username = identity.get('username')
            if not username:
                username = request['headers']['x-api-key']
            connected_edges = ogm.get_edge_connection(username, args, source)
            return connected_edges
