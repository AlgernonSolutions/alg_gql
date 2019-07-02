import logging

from aws_xray_sdk.core import xray_recorder

from toll_booth.obj.graph.ogm import Ogm

known_fields = ('connected_edges',)


@xray_recorder.capture('vertex')
def handler(type_name, field_name, args, source, result, request, identity):
    ogm = Ogm()
    if type_name == 'Vertex':
        if field_name == 'connected_edges':
            logging.debug('request resolved to Vertex.connected_edges')
            internal_id = source.get('internal_id')
            edge_labels = args.get('edge_labels')
            connected_edges = ogm.query_edge_connections(internal_id, edge_labels)
            return connected_edges
