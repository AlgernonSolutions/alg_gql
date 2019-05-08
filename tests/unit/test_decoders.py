import pytest
import rapidjson

from toll_booth.obj.graph.serializers import GqlDecoder
from toll_booth.obj.graph.trident.connections import TridentDecoder
from algernon import ajson


@pytest.mark.trident_decoder
class TestTridentDecoder:
    def test_decode_vertex(self, db_get_vertex_response):
        results = rapidjson.loads(rapidjson.dumps(db_get_vertex_response), object_hook=TridentDecoder.object_hook)
        assert results

    def test_decode_vertex_properties(self, db_vertex_vertex_properties_response):
        results = rapidjson.loads(rapidjson.dumps(db_vertex_vertex_properties_response), object_hook=TridentDecoder.object_hook)
        assert results


@pytest.mark.gql_decoder
class TestGqlDecoder:
    def test_gql_decoder(self, db_get_vertex_response):
        vertex = rapidjson.loads(rapidjson.dumps(db_get_vertex_response), object_hook=TridentDecoder.object_hook)
        vertex_string = ajson.dumps(vertex)
        gql = rapidjson.loads(vertex_string, object_hook=GqlDecoder.object_hook)
        assert gql

    def test_vertex_vertex_properties(self, db_vertex_vertex_properties_response):
        vertex_properties = rapidjson.loads(
            rapidjson.dumps(db_vertex_vertex_properties_response), object_hook=TridentDecoder.object_hook)
        vertex_properties_string = ajson.dumps(vertex_properties)
        gql = rapidjson.loads(vertex_properties_string, object_hook=GqlDecoder.object_hook)
        assert gql

    def test_add_vertex_response(self, db_add_vertex_response):
        vertex = rapidjson.loads(
            rapidjson.dumps(db_add_vertex_response), object_hook=TridentDecoder.object_hook)
        vertex_string = ajson.dumps(vertex)
        gql = rapidjson.loads(vertex_string, object_hook=GqlDecoder.object_hook)
        assert gql
