import pytest

from toll_booth import handler


@pytest.mark.tasks
@pytest.mark.usefixtures('unit_test_environment')
class TestGraphObject:
    def test_query_edge_connection(self, test_event, mock_context, mocks):
        event = test_event('edge_connection_edges')
        results = handler(event, mock_context)
        assert results

    def test_paginated_query(self, test_event, mock_context, mocks):
        event = test_event('maltego_query_vertex')
        results = handler(event, mock_context)
        assert results

    def test_query_edges_filtered(self, test_event, mock_context, mocks):
        event = test_event('get_edge_filtered')
        results = handler(event, mock_context)
        assert results

    def test_graph_cluster(self, graph_cluster_event, mock_context, mocks):
        results = handler(graph_cluster_event, mock_context)
        assert results

    def test_graph_object(self, graph_vertex_event, mock_context, mocks):
        event = graph_vertex_event('vertex_connected_edges')
        results = handler(event, mock_context)
        assert results
