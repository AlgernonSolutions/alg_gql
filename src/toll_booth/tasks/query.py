from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.index.index_manager import IndexManager
from toll_booth.obj.troubles import InvalidGqlRequestException


known_fields = ('vertex')


def handler(type_name, field_name, args, source, result, request):
    if type_name == 'Query':
        ogm = Ogm()
        index_manager = IndexManager()
        if field_name == 'vertex':
            internal_id = args.get('internal_id', None)
            if internal_id is None:
                raise InvalidGqlRequestException(type_name, field_name, ['internal_id'])
            vertex = ogm.query_vertex(internal_id)
            return vertex
