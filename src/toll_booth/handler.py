import logging
import os

import boto3
import rapidjson
from algernon import ajson
from algernon.aws import lambda_logged
from algernon.aws.task_setup import stated, rebuild_event
from aws_xray_sdk.core import xray_recorder

from toll_booth.obj.graph.serializers import GqlDecoder
from toll_booth.tasks import mutation, vertex, edge_connection, query


ENVIRON_VARIABLES = [
    'ALGERNON_BUCKET_NAME',
    'STORAGE_BUCKET_NAME',
    'ENCOUNTER_BUCKET_NAME',
    'GRAPH_GQL_ENDPOINT',
    'GRAPH_DB_ENDPOINT',
    'GRAPH_DB_READER_ENDPOINT',
    'INDEX_TABLE_NAME',
    'SENSITIVE_TABLE_NAME',
    'PROGRESS_TABLE_NAME',
    'FIRE_HOSE_NAME'
]


def _load_config(variable_names):
    client = boto3.client('ssm')
    response = client.get_parameters(Names=[x for x in variable_names])
    results = [(x['Name'], x['Value']) for x in response['Parameters']]
    for entry in results:
        os.environ[entry[0]] = entry[1]


def _decision_tree(type_name, field_name, args, source, result, request, identity):
    decision_args = (type_name, field_name, args, source, result, request, identity)
    if type_name == 'Vertex':
        if field_name in vertex.known_fields:
            return vertex.handler(*decision_args)
    if type_name == 'Mutation':
        if field_name in mutation.known_fields:
            return mutation.handler(*decision_args)
    if type_name == 'EdgeConnection':
        if field_name in edge_connection.known_fields:
            return edge_connection.handler(*decision_args)
    if type_name == 'Query':
        return query.handler(*decision_args)
    raise RuntimeError(f'could not resolve how to deal with {type_name}.{field_name}')


@lambda_logged
@xray_recorder.capture('alg_gql')
def handler(event, context):
    logging.info(f'received a call to run a graph_object command: event/context: {event}/{context}')
    _load_config(ENVIRON_VARIABLES)
    if isinstance(event, list):
        results = []
        for entry in event:
            result = handler(entry, context)
            results.append(result)
        return results
    gql_context = event['context']
    field_name = event['field_name']
    type_name = event['type_name']
    args = gql_context['arguments']
    source = gql_context['source']
    result = gql_context['result']
    request = gql_context['request']
    identity = gql_context['identity']

    results = _decision_tree(type_name, field_name, args, source, result, request, identity)
    logging.debug(f'results after the decision tree: {results}')
    strung_results = ajson.dumps(results)
    logging.debug(f'results after first round of json encoding: {strung_results}')
    encoded_results = rapidjson.loads(strung_results, object_hook=GqlDecoder.object_hook)
    logging.info(f'results after GQL encoding: {encoded_results}')
    return encoded_results


@lambda_logged
@stated
@xray_recorder.capture('alg_gql_sfn')
def sfn_handler(event, context):
    event = rebuild_event(event)
    logging.info(f'received a call to run graphing operation, sfn mode: {event}/{context}')
    task_kwargs = event['task_kwargs']
    type_name = task_kwargs['type_name']
    field_name = task_kwargs['field_name']
    args = task_kwargs['args']
    return mutation.handler(type_name, field_name, args, {}, {}, {}, {})
