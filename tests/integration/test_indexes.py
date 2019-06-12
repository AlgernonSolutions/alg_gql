import os

import pytest

from toll_booth.obj.graph.gql_scalars.object_properties import ObjectProperty, LocalPropertyValue
from toll_booth.obj.index.index_manager import IndexManager


@pytest.mark.integration_index
class TestIndexes:
    def test_index_scan(self):
        os.environ['INDEX_TABLE_NAME'] = 'Indexes'
        index_manager = IndexManager()
        vertex_properties = [
            ObjectProperty('id_source', LocalPropertyValue('Algernon', 'S')),
            ObjectProperty('id_type', LocalPropertyValue('Employees', 'S'))
        ]
        found_vertexes = index_manager.find_potential_vertexes('MockVertex', vertex_properties)
        assert found_vertexes
