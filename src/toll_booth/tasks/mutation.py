import logging
from multiprocessing.dummy import Pool as ThreadPool
from typing import Union

from toll_booth.obj.graph.ogm import Ogm
from toll_booth.obj.graph.gql_scalars import InputVertex, InputEdge
from toll_booth.obj.index.index_manager import IndexManager
from toll_booth.obj.index.troubles import UniqueIndexViolationException


def _graph_vertex(vertex_scalar: InputVertex):
    logging.info(f'started the graph vertex operation for: {vertex_scalar}')
    ogm = Ogm()
    graph_results = ogm.graph_vertex(vertex_scalar)
    logging.info(f'completed the graph vertex operation for: {vertex_scalar}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


def _delete_graphed_vertex(internal_id: str):
    logging.info(f'started the delete graphed vertex operation for: {internal_id}')
    ogm = Ogm()
    graph_results = ogm.delete_vertex(internal_id)
    logging.info(f'completed the delete graphed vertex operation for: {internal_id}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


def _graph_edge(edge_scalar: InputEdge):
    logging.info(f'started the graph edge operation for: {edge_scalar}')
    ogm = Ogm()
    graph_results = ogm.graph_edge(edge_scalar)
    logging.info(f'completed the graph edge operation for: {edge_scalar}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


def _delete_graphed_edge(internal_id: str):
    logging.info(f'started the delete graphed edge operation for: {internal_id}')
    ogm = Ogm()
    graph_results = ogm.delete_edge(internal_id)
    logging.info(f'completed the delete graphed edge operation for: {internal_id}, results: {graph_results}')
    results = {'graph_results': graph_results}
    return results


def _index_object(gql_scalar: Union[InputVertex, InputEdge]):
    logging.info(f'started the index object operation for: {gql_scalar}')
    index_manager = IndexManager()
    try:
        index_results = index_manager.index_object(gql_scalar)
    except UniqueIndexViolationException as e:
        logging.warning(f'attempted to index {gql_scalar}, it seems it has already been indexed: {e.index_name}')
        index_results = f'object: {gql_scalar} indexed already, nothing done'
    logging.info(f'completed the index object operation for: {gql_scalar}, results: {index_results}')
    results = {'index_results': index_results}
    return results


def _delete_indexed_object(internal_id: str):
    logging.info(f'started the delete indexed object operation for: {internal_id}')
    index_manager = IndexManager()
    index_results = index_manager.delete_object(internal_id)
    logging.info(f'completed the delete indexed object operation for: {internal_id}, results: {index_results}')
    results = {'index_results': index_results}
    return results


def _work(*args):
    fn = args[0][0]
    gql_scalar = args[0][1]
    return fn(gql_scalar)


def _add_vertex(vertex_scalar: InputVertex):
    logging.info(f'starting the add_vertex operation for: {vertex_scalar}')
    results = {}
    operations = [(_graph_vertex, vertex_scalar), (_index_object, vertex_scalar)]
    pool = ThreadPool(2)
    map_results = pool.map(_work, operations)
    pool.close()
    pool.join()
    for entry in map_results:
        results.update(entry)
    logging.info(f'the results from the two components of the add_vertex operation are: {results}')
    return results


def _delete_vertex(internal_id: str):
    logging.info(f'starting the delete_vertex operation for: {internal_id}')
    results = {}
    operations = [(_delete_graphed_vertex, internal_id), (_delete_indexed_object, internal_id)]
    pool = ThreadPool(2)
    map_results = pool.map(_work, operations)
    pool.close()
    pool.join()
    for entry in map_results:
        results.update(entry)
    logging.info(f'the results from the two components of the delete_vertex operation are: {results}')
    return results


def _delete_edge(internal_id: str):
    logging.info(f'starting the delete_edge operation for: {internal_id}')
    results = {}
    operations = [(_delete_graphed_edge, internal_id), (_delete_indexed_object, internal_id)]
    pool = ThreadPool(2)
    map_results = pool.map(_work, operations)
    pool.close()
    pool.join()
    for entry in map_results:
        results.update(entry)
    logging.info(f'the results from the two components of the delete_edge operation are: {results}')
    return results


def _add_edge(edge_scalar: InputEdge):
    logging.info(f'starting the add_edge operation for: {edge_scalar}')
    results = {}
    operations = [(_graph_edge, edge_scalar), (_index_object, edge_scalar)]
    pool = ThreadPool(2)
    map_results = pool.map(_work, operations)
    pool.close()
    pool.join()
    for entry in map_results:
        results.update(entry)
    logging.info(f'the results from the two components of the add_edge operation are: {results}')
    return results


known_fields = ('delete_vertex', 'delete_edge', 'add_vertex', 'add_edge')


def handler(type_name, field_name, args, source, result, request, identity):
    if type_name == 'Mutation':
        if field_name == 'delete_vertex':
            logging.info(f'request resolved to Mutation.deleteVertex')
            internal_id = args['internal_id']
            results = _delete_vertex(internal_id)
            logging.info(f'completed an deleteVertex command, results: {results}')
            return results
        if field_name == 'delete_edge':
            logging.info(f'request resolved to Mutation.deleteEdge')
            internal_id = args['internal_id']
            results = _delete_edge(internal_id)
            logging.info(f'completed an deleteEdge command, results: {results}')
            return results
        if field_name == 'add_vertex':
            logging.info(f'request resolved to Mutation.addVertex')
            vertex_scalar = InputVertex.from_arguments(args['vertex'])
            logging.info(f'generated the vertex scalar for Mutation.addVertex: {vertex_scalar}')
            results = _add_vertex(vertex_scalar)
            logging.info(f'completed an addVertex command, results: {results}')
            return results
        if field_name == 'add_edge':
            logging.info(f'request resolved to Mutation.addEdge')
            edge_scalar = InputEdge.from_arguments(args['edge'])
            logging.info(f'generated the edge scalar for Mutation.addEdge: {edge_scalar}')
            results = _add_edge(edge_scalar)
            logging.info(f'completed an addEdge command, results: {results}')
            return results
