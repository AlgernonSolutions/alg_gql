import os

import pytest

from toll_booth import tasks
from toll_booth.tasks import mutation


@pytest.mark.integration_tasks
@pytest.mark.usefixtures('integration_test_environment')
class TestTasks:
    def test_graph_edge_graph_i(self, mock_input_edge, mocks):
        results = mutation._graph_edge(mock_input_edge)
        assert results

    def test_graph_vertex_index_i(self, mock_input_vertex, mocks):
        results = mutation._index_object(mock_input_vertex)
        assert results

    def test_graph_vertex_graph_i(self, mock_input_vertex, mocks):
        results = mutation._graph_vertex(mock_input_vertex)
        assert results

    def test_query_vertex_i(self, graph_vertex_event, mock_context):
        event = graph_vertex_event('check_for_existing_vertexes')
        results = tasks.ogm(event, mock_context)
        assert results

    def test_query_vertex_properties_i(self, test_event, mock_context):
        event = test_event('query_vertex_properties')
        results = tasks.ogm(event, mock_context)
        assert results

    @pytest.mark.query_connected_edges_i
    def test_query_vertex_connected_edges_i(self, test_event, mock_context):
        event = test_event('vertex_connected_edges')
        results = tasks.ogm(event, mock_context)
        assert results
