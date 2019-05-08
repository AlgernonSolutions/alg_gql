import json
from datetime import datetime
from os import path
from unittest.mock import patch

import pytest

_mock_vertex_data = {
    'internal_id': '12443kdkg23345912493sfdsfs',
    'id_value': 1001,
    'identifier_stem': 'some_id_source#some_id_type#some_id_name',
    'vertex_type': 'MockVertex',
    'vertex_properties': [
        {
            'property_name': 'id_source',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_source',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_type',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_type',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_name',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_name',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_value',
            'property_value': {
                'data_type': 'Number',
                'property_value': '1001',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'some_date_time_value',
            'property_value': {
                'data_type': 'DateTime',
                'property_value': str(datetime.now().timestamp()),
                'is_sensitive': False
            }
        }
    ]
}

_mock_edge_data = {
    'internal_id': '12443kdkg23345912493sfdsfs',
    'id_value': 1001,
    'identifier_stem': 'some_id_source#some_id_type#some_id_name',
    'source_vertex_internal_id': '1234325436dwgds46d',
    'target_vertex_internal_id': '123sdfsvsdfyfdt4asf',
    'edge_label': '_mock_edge_',
    'edge_properties': [
        {
            'property_name': 'id_source',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_source',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_type',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_type',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_name',
            'property_value': {
                'data_type': 'String',
                'property_value': 'some_id_name',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'id_value',
            'property_value': {
                'data_type': 'Number',
                'property_value': '1001',
                'is_sensitive': False
            }
        },
        {
            'property_name': 'some_date_time_value',
            'property_value': {
                'data_type': 'DateTime',
                'property_value': str(datetime.now().timestamp()),
                'is_sensitive': False
            }
        }
    ]
}


@pytest.fixture
def db_get_vertex_response():
    return _read_test_event('get_vertex', 'graph_responses')


@pytest.fixture
def db_vertex_vertex_properties_response():
    return _read_test_event('get_vertex_properties', 'graph_responses')


@pytest.fixture
def db_add_vertex_response():
    return _read_test_event('add_vertex', 'graph_responses')


@pytest.fixture
def mock_vertex_data():
    return _mock_vertex_data


@pytest.fixture
def mock_edge_data():
    return _mock_edge_data


@pytest.fixture
def graph_vertex_event():
    return _read_test_event


@pytest.fixture(autouse=True)
def silence_x_ray():
    x_ray_patch_all = 'algernon.aws.lambda_logging.patch_all'
    patch(x_ray_patch_all).start()
    yield
    patch.stopall()


@pytest.fixture
def mock_ogm():
    ogm_path = 'toll_booth.obj.graph.ogm.TridentDriver'
    secrets_dynamo_path = 'toll_booth.obj.graph.gql_scalars.boto3'
    index_dynamo_path = 'toll_booth.obj.index.index_manager.boto3'
    mock_secrets_dynamo = patch(secrets_dynamo_path).start()
    mock_index_dynamo = patch(index_dynamo_path).start()
    mock_ogm = patch(ogm_path).start()
    yield mock_ogm, mock_secrets_dynamo, mock_index_dynamo
    patch.stopall()


@pytest.fixture
def mock_context():
    from unittest.mock import MagicMock
    context = MagicMock(name='context')
    context.__reduce__ = cheap_mock
    context.function_name = 'test_function'
    context.invoked_function_arn = 'test_function_arn'
    context.aws_request_id = '12344_request_id'
    context.get_remaining_time_in_millis.side_effect = [1000001, 500001, 250000, 0]
    return context


def cheap_mock(*args):
    from unittest.mock import Mock
    return Mock, ()


def _read_test_event(event_name, sub_category=None):
    event_path = path.join('tests', 'test_events', f'{event_name}.json')
    if sub_category:
        event_path = path.join('tests', 'test_events', sub_category, f'{event_name}.json')
    with open(event_path) as json_file:
        event = json.load(json_file)
        return event
