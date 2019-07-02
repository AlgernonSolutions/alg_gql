import logging
from typing import Union

import boto3
from aws_xray_sdk.core import xray_recorder

from toll_booth.obj.graph.gql_scalars.inputs import InputVertex, InputEdge
from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.index.index_manager import IndexManager
from toll_booth.obj.index.troubles import UniqueIndexViolationException

known_fields = (
    'add_vertex', 'add_edge',
    'delete_vertex', 'delete_edge',
    'delete_vertex_index', 'delete_vertex_graph',
    'delete_edge_index', 'delete_edge_graph',
    'add_vertex_index', 'add_vertex_graph',
    'add_edge_index', 'add_edge_graph'
)


@xray_recorder.capture()
def _graph_vertex(vertex_scalar: InputVertex):
    logging.debug(f'started the graph vertex operation for: {vertex_scalar}')
    ogm = Ogm()
    graph_results = ogm.graph_vertex(vertex_scalar)
    logging.debug(f'completed the graph vertex operation for: {vertex_scalar}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


@xray_recorder.capture()
def _delete_graphed_vertex(internal_id: str):
    logging.debug(f'started the delete graphed vertex operation for: {internal_id}')
    ogm = Ogm()
    graph_results = ogm.delete_vertex(internal_id)
    logging.debug(f'completed the delete graphed vertex operation for: {internal_id}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


@xray_recorder.capture()
def _graph_edge(edge_scalar: InputEdge):
    logging.debug(f'started the graph edge operation for: {edge_scalar}')
    ogm = Ogm()
    graph_results = ogm.graph_edge(edge_scalar)
    logging.debug(f'completed the graph edge operation for: {edge_scalar}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


@xray_recorder.capture()
def _delete_graphed_edge(internal_id: str):
    logging.debug(f'started the delete graphed edge operation for: {internal_id}')
    ogm = Ogm()
    graph_results = ogm.delete_edge(internal_id)
    logging.debug(f'completed the delete graphed edge operation for: {internal_id}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


@xray_recorder.capture()
def _index_object(gql_scalar: Union[InputVertex, InputEdge]):
    logging.debug(f'started the index object operation for: {gql_scalar}')
    index_manager = IndexManager()
    try:
        index_results = index_manager.index_object(gql_scalar)
    except UniqueIndexViolationException as e:
        logging.warning(f'attempted to index {gql_scalar}, it seems it has already been indexed: {e.index_name}')
        index_results = f'object: {gql_scalar} indexed already, nothing done'
    logging.debug(f'completed the index object operation for: {gql_scalar}, results: {index_results}')
    results = {'index_results': index_results}
    return results


@xray_recorder.capture()
def _delete_indexed_object(internal_id: str):
    logging.debug(f'started the delete indexed object operation for: {internal_id}')
    index_manager = IndexManager()
    index_results = index_manager.delete_object(internal_id)
    logging.debug(f'completed the delete indexed object operation for: {internal_id}, results: {index_results}')
    results = {'index_results': index_results}
    return results


@xray_recorder.capture()
def _delete_vertex(internal_id):
    pass


@xray_recorder.capture()
def _delete_edge(internal_id):
    pass


@xray_recorder.capture()
def _add_vertex(vertex_args):
    pass


@xray_recorder.capture()
def _add_edge(edge_args):
    pass


@xray_recorder.capture('mutation')
def handler(type_name, field_name, args, source, result, request, identity):
    if type_name == 'Mutation':
        if field_name == 'delete_vertex':
            internal_id = args['internal_id']
            return _delete_vertex(internal_id)
        if field_name == 'delete_edge':
            internal_id = args['internal_id']
            return _delete_vertex(internal_id)
        if field_name == 'add_vertex':
            vertex_args = args['vertex']
            return _add_vertex(vertex_args)
        if field_name == 'add_edge':
            edge_args = args['edge']
            return _add_edge(edge_args)
        if field_name == 'delete_vertex_index':
            logging.debug(f'request resolved to Mutation.deleteVertex_index')
            internal_id = args['internal_id']
            results = _delete_indexed_object(internal_id)
            logging.debug(f'completed an deleteVertex_index command, results: {results}')
            return results
        if field_name == 'delete_vertex_graph':
            logging.debug(f'request resolved to Mutation.deleteVertex_graph')
            internal_id = args['internal_id']
            results = _delete_graphed_vertex(internal_id)
            logging.debug(f'completed an deleteVertex_graph command, results: {results}')
            return results
        if field_name == 'delete_edge_index':
            logging.debug(f'request resolved to Mutation.deleteEdge_index')
            internal_id = args['internal_id']
            results = _delete_indexed_object(internal_id)
            logging.debug(f'completed an deleteEdge_index command, results: {results}')
            return results
        if field_name == 'delete_edge_graph':
            logging.debug(f'request resolved to Mutation.deleteEdge_graph')
            internal_id = args['internal_id']
            results = _delete_graphed_edge(internal_id)
            logging.debug(f'completed an deleteEdge_graph command, results: {results}')
            return results
        if field_name == 'add_vertex_index':
            logging.debug(f'request resolved to Mutation.addVertex_index')
            vertex_scalar = InputVertex.from_arguments(args['vertex'])
            logging.debug(f'generated the vertex scalar for Mutation.addVertex_index: {vertex_scalar}')
            results = _index_object(vertex_scalar)
            logging.debug(f'completed an addVertex command, results: {results}')
            return True
        if field_name == 'add_vertex_graph':
            logging.debug(f'request resolved to Mutation.addVertex_graph')
            vertex_scalar = InputVertex.from_arguments(args['vertex'])
            logging.debug(f'generated the vertex scalar for Mutation.addVertex_graph: {vertex_scalar}')
            results = _graph_vertex(vertex_scalar)
            logging.debug(f'completed an addVertex_graph command, results: {results}')
            return True
        if field_name == 'add_edge_index':
            logging.debug(f'request resolved to Mutation.addEdge_index')
            edge_scalar = InputEdge.from_arguments(args['edge'])
            logging.debug(f'generated the edge scalar for Mutation.addEdge_index: {edge_scalar}')
            results = _index_object(edge_scalar)
            logging.debug(f'completed an addEdge_index command, results: {results}')
            return True
        if field_name == 'add_edge_graph':
            logging.debug(f'request resolved to Mutation.addEdge_graph')
            edge_scalar = InputEdge.from_arguments(args['edge'])
            logging.debug(f'generated the edge scalar for Mutation.addEdge_graph: {edge_scalar}')
            results = _graph_edge(edge_scalar)
            logging.debug(f'completed an addEdge_graph command, results: {results}')
            return True
