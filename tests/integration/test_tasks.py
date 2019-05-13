import os

import pytest

from toll_booth import tasks


@pytest.mark.integration_tasks
@pytest.mark.usefixtures('integration_test_environment')
class TestTasks:
    def test_query_vertex(self, graph_vertex_event, mock_context):
        event = graph_vertex_event('query_vertex')
        results = tasks.ogm(event, mock_context)
        assert results

    def test_query_vertex_properties(self, test_event, mock_context):
        event = test_event('query_vertex_properties')
        results = tasks.ogm(event, mock_context)
        assert results

    def test_query_vertex_connected_edges(self, test_event, mock_context):
        event = test_event('vertex_connected_edges')
        results = tasks.ogm(event, mock_context)
        assert results
