import logging
from typing import Dict, List, Any

import rapidjson

from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.graph.trident.trident_obj.properties import TridentProperty

from toll_booth.obj.troubles import InvalidGqlRequestException


known_fields = ('vertex_properties', 'connected_edges')


def compile_object_properties(trident_properties: Dict[str, List[TridentProperty]]):
    gql_properties = []
    for property_name, trident_property in trident_properties.items():
        property_value = parse_object_properties(property_name, trident_property)
        if property_name in ['id_value', 'identifier_stem']:
            continue
        gql_properties.append(property_value)
    return gql_properties


def _parse_property_value(property_attributes: List[Any]) -> Dict[str, Any]:
    if len(property_attributes) > 2:
        raise RuntimeError(f'received property attributes: {property_attributes}, '
                           f'but there are too many, should be two')
    for property_attribute in property_attributes:
        try:
            return rapidjson.loads(property_attribute)
        except (ValueError, TypeError):
            continue
    raise NotImplementedError(f'could not parse trident property for property_attributes: {property_attributes}')


def parse_object_properties(property_name: str, object_properties: List[TridentProperty]) -> Dict[str, Any]:
    property_attributes = []
    for object_property in object_properties:
        property_attributes.append(object_property.value)
    gql = {
        '__typename': 'ObjectProperty',
        'property_name': property_name,
        'property_value': _parse_property_value(property_attributes)
    }
    return gql


def handler(type_name, field_name, args, source, result, request, identity):
    ogm = Ogm()
    if type_name == 'Vertex':
        if field_name == 'vertex_properties':
            logging.info(f'request resolved to Vertex.vertex_properties')
            internal_id = source.get('internal_id', None)
            if internal_id is None:
                raise InvalidGqlRequestException(type_name, field_name, ['internal_id'])
            vertex_properties = ogm.query_vertex_properties(internal_id)
            if len(vertex_properties) > 1:
                raise RuntimeError(f'queried vertex properties, '
                                   f'got more responses than we should have: {vertex_properties}')
            for entry in vertex_properties:
                gql_properties = compile_object_properties(entry)
                logging.info(f'completed an vertex_properties command, results: {gql_properties}')
                return gql_properties
            return []
        if field_name == 'connected_edges':
            logging.info('request resolved to Vertex.connected_edges')
            if identity in ('None', None):
                identity = {}
                logging.warning(f'processed request for Vertex.connected_edges, no identity provided,'
                                f'this is ok for development, but should not occur in production')
            username = identity.get('username', request['headers']['x-api-key'])
            connected_edges = ogm.get_edge_connection(username, args, source)
            return connected_edges
