from toll_booth.obj.graph.gql_scalars.inputs import InputVertex, InputEdge


class TestVertex:
    def test_vertex_creation(self, mock_vertex_data):
        vertex = InputVertex.from_json(mock_vertex_data)
        assert isinstance(vertex, InputVertex)
        assert hasattr(vertex, 'vertex_type')
        assert hasattr(vertex, 'vertex_properties')
        assert vertex.object_class == 'Vertex'
        assert vertex.for_index
        assert isinstance(vertex.numeric_id_value, int)


class TestEdge:
    def test_edge_creation(self, mock_edge_data):
        edge = InputEdge.from_json(mock_edge_data)
        assert isinstance(edge, InputEdge)
        assert hasattr(edge, 'edge_label')
        assert hasattr(edge, 'edge_properties')
        assert edge.object_class == 'Edge'
        assert edge.for_index
