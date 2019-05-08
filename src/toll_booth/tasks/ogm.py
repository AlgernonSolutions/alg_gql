import logging

import rapidjson
from algernon import ajson
from algernon.aws import lambda_logged

from toll_booth.obj.graph.serializers import GqlDecoder
from toll_booth.tasks import mutation, query, vertex


def _decision_tree(type_name, field_name, args, source, result, request):
    decision_args = (type_name, field_name, args, source, result, request)
    if type_name == 'Vertex':
        if field_name in vertex.known_fields:
            return vertex.handler(*decision_args)
    if type_name == 'Query':
        if field_name in query.known_fields:
            return query.handler(*decision_args)
    if type_name == 'Mutation':
        if field_name in mutation.known_fields:
            return mutation.handler(*decision_args)
    raise RuntimeError(f'could not resolve how to deal with {type_name}.{field_name}')


@lambda_logged
def handler(event, context):
    logging.info(f'received a call to run a graph_object command: event/context: {event}/{context}')
    gql_context = event['context']
    field_name = event['field_name']
    type_name = event['type_name']
    args = gql_context['arguments']
    source = gql_context['source']
    result = gql_context['result']
    request = gql_context['request']

    results = _decision_tree(type_name, field_name, args, source, result, request)
    return rapidjson.loads(ajson.dumps(results), object_hook=GqlDecoder.object_hook)
