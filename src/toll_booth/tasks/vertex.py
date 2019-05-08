import logging
from typing import Dict, List, Any

from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.graph.trident.trident_obj.properties import TridentProperty

from toll_booth.obj.troubles import InvalidGqlRequestException


known_fields = ('vertex_properties')


def compile_object_properties(trident_properties: Dict[str, List[TridentProperty]]):
    gql_properties = []
    for property_name, trident_property in trident_properties.items():
        property_value = parse_object_properties(property_name, trident_property)
        if property_name in ['id_value', 'identifier_stem']:
            continue
        gql_properties.append(property_value)
    return gql_properties


def _parse_property_value(property_attributes: List[Any]) -> Dict[str, Any]:
    property_value = property_attributes[0]
    property_data_type = property_attributes[1]
    property_class = property_attributes[2]
    if property_class == 'SensitivePropertyValue':
        return {
            '__typename': property_class,
            'pointer': property_value,
            'data_type': property_data_type,
        }
    if property_class == 'LocalPropertyValue':
        return {
            '__typename': property_class,
            'property_value': property_value,
            'data_type': property_data_type,
        }
    if property_class == 'StoredPropertyValue':
        return {
            '__typename': property_class,
            'storage_uri': property_value,
            'data_type': property_data_type,
            'storage_class': property_attributes[3]
        }
    raise NotImplementedError(f'could not parse trident property for property_class: {property_class}')


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


def handler(type_name, field_name, args, source, result, request):
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
