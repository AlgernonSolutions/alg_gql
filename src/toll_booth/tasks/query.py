from aws_xray_sdk.core import xray_recorder

from toll_booth.obj.graph.ogm import Ogm


@xray_recorder.capture('query')
def handler(type_name, field_name, args, source, result, request, identity):
    ogm = Ogm()
    query_text = args['query_text']
    return ogm.run_read_query(query_text)
