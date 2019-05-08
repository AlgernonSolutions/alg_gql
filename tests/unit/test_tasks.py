import os

import pytest

from toll_booth import tasks


@pytest.mark.tasks
class TestGraphObject:
    def test_graph_object(self, graph_vertex_event, mock_context, mock_ogm):
        event = graph_vertex_event('add_vertex')
        os.environ['GRAPH_DB_ENDPOINT'] = 'algernon.cluster-cnv3iqiknsnm.us-east-1.neptune.amazonaws.com'
        os.environ['GRAPH_DB_READER_ENDPOINT'] = 'algernon.cluster-ro-cnv3iqiknsnm.us-east-1.neptune.amazonaws.com'
        os.environ['SENSITIVES_TABLE_NAME'] = 'Secrets'
        os.environ['INDEX_TABLE_NAME'] = 'Index'
        results = tasks.ogm(event, mock_context)
        assert results
