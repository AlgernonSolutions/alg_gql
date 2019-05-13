from typing import Dict, Any

from toll_booth.obj.graph.gql_scalars import ObjectProperty, LocalPropertyValue
from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.index.index_manager import IndexManager
from toll_booth.obj.troubles import InvalidGqlRequestException


known_fields = ('vertex', 'find_vertexes')


def handler(type_name: str,
            field_name: str,
            args: Dict[str, Any],
            source: Dict[str, Any],
            result: Dict[str, Any],
            request: Dict[str, Any],
            identity: Dict[str, Any]) -> Any:
    if type_name == 'Query':
        ogm = Ogm()
        index_manager = IndexManager()
        if field_name == 'vertex':
            internal_id = args.get('internal_id', None)
            if internal_id is None:
                raise InvalidGqlRequestException(type_name, field_name, ['internal_id'])
            vertex = ogm.query_vertex(internal_id)
            return vertex
        if field_name == 'find_vertexes':
            object_type = args.get('object_type')
            search_properties = args.get('object_properties')
            if object_type is None or search_properties is None:
                raise InvalidGqlRequestException(type_name, field_name, ['object_type', 'object_properties'])
            local_properties = [
                ObjectProperty(x['property_name'], LocalPropertyValue.parse_json(x)) for x in search_properties]
            return index_manager.find_potential_vertexes(object_type, local_properties)
