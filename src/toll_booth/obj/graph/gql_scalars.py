import hashlib
import logging
from decimal import Decimal
from typing import List, Union, Dict

import boto3
import dateutil
from algernon import AlgObject
from botocore.exceptions import ClientError

from toll_booth.obj.graph.troubles import SensitiveValueAlreadyStored


class StoredPropertyValue(AlgObject):
    def __init__(self, storage_uri, storage_class, data_type):
        self._storage_uri = storage_uri
        self._storage_class = storage_class
        self._data_type = data_type

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['storage_uri'], json_dict['storage_class'], json_dict['data_type'])

    @property
    def property_value(self):
        return self._storage_uri

    @property
    def storage_uri(self):
        return self._storage_uri

    @property
    def storage_class(self):
        return self._storage_class

    @property
    def data_type(self):
        return self._data_type

    @property
    def for_index(self):
        return {
            'data_type': self._data_type,
            'storage_uri': self._storage_uri,
            'storage_class': self._storage_class,
            'property_type': type(self).__name__
        }


class SensitivePropertyValue(AlgObject):
    def __init__(self,
                 property_name: str,
                 sensitive_value: str,
                 insensitive_pointer: str,
                 data_type: str):
        self._sensitive_value = sensitive_value
        self._insensitive_pointer = insensitive_pointer
        self._data_type = data_type
        self._property_name = property_name

    @classmethod
    def parse_json(cls, json_dict: Dict):
        return cls(
            json_dict['property_name'], json_dict['sensitive_value'],
            json_dict['insensitive_pointer'], json_dict['data_type'])

    @classmethod
    def generate_from_raw(cls,
                          source_internal_id: str,
                          property_name: str,
                          sensitive_property_value: str,
                          data_type: str):
        """Creates a pointer and stores the sensitive value into the secrets vault

        Args:
            source_internal_id:
            property_name:
            sensitive_property_value:
            data_type:

        Returns:

        """
        logging.info(f'starting to generate a SensitiveProperty from raw: {source_internal_id}, {property_name}')
        try:
            insensitive_pointer = _update_sensitive_data(source_internal_id, property_name, sensitive_property_value)
        except SensitiveValueAlreadyStored:
            insensitive_pointer = _create_sensitive_pointer(property_name, source_internal_id)
        return cls(property_name, sensitive_property_value, insensitive_pointer, data_type)

    @property
    def sensitive_value(self) -> str:
        return self._sensitive_value

    @property
    def data_type(self) -> str:
        return self._data_type

    @property
    def for_index(self):
        property_value = _set_property_value_data_type(self._insensitive_pointer, 'S')
        return {
            'data_type': self._data_type,
            'pointer': property_value,
            'property_type': type(self).__name__
        }

    @property
    def property_value(self) -> str:
        return self._insensitive_pointer


class LocalPropertyValue(AlgObject):
    def __init__(self, property_value, data_type):
        self._property_value = property_value
        self._data_type = data_type

    @classmethod
    def parse_json(cls, json_dict):
        return cls(json_dict['property_value'], json_dict['data_type'])

    @property
    def property_value(self):
        property_value = _set_property_value_data_type(self._property_value, self._data_type)
        return property_value

    @property
    def data_type(self):
        return self._data_type

    @property
    def for_index(self):
        return {
            'data_type': self._data_type,
            'property_value': self.property_value,
            'property_type': type(self).__name__
        }


class ObjectProperty(AlgObject):
    def __init__(self,
                 property_name: str,
                 property_value: Union[StoredPropertyValue, LocalPropertyValue, SensitivePropertyValue]):
        self._property_name = property_name
        self._property_value = property_value

    @classmethod
    def parse_json(cls, json_dict: Dict):
        return cls(json_dict['property_name'], json_dict['property_value'])

    @property
    def property_name(self):
        return self._property_name

    @property
    def property_value(self):
        return self._property_value

    @property
    def for_index(self):
        return {
            'property_name': self._property_name,
            'property_value': self._property_value.for_index
        }


class GraphScalar:
    def __init__(self,
                 internal_id: str,
                 object_type: str,
                 id_value: ObjectProperty,
                 identifier_stem: ObjectProperty,
                 object_properties: List[ObjectProperty] = None):
        if not object_properties:
            object_properties = []
        self._internal_id = internal_id
        self._object_type = object_type
        self._id_value = id_value
        self._identifier_stem = identifier_stem
        self._object_properties = object_properties

    @property
    def internal_id(self) -> str:
        return self._internal_id

    @property
    def object_type(self) -> str:
        return self._object_type

    @property
    def id_value(self) -> ObjectProperty:
        return self._id_value

    @property
    def identifier_stem(self) -> ObjectProperty:
        return self._identifier_stem

    @property
    def object_properties(self) -> List[ObjectProperty]:
        return self._object_properties

    @property
    def _for_index(self):
        id_value = self._id_value.property_value.property_value
        identifier_stem = self._identifier_stem.property_value.property_value
        indexed_value = {
            'sid_value': str(id_value),
            'identifier_stem': str(identifier_stem),
            'internal_id': str(self._internal_id),
            'id_value': id_value,
            'object_type': self._object_type,
            'object_class': self.object_class
        }
        if isinstance(id_value, int) or isinstance(id_value, Decimal):
            indexed_value['numeric_id_value'] = id_value
        for object_property in self._object_properties:
            property_name = object_property.property_name
            if property_name not in indexed_value:
                indexed_value[property_name] = object_property.for_index
        return indexed_value

    @property
    def object_class(self):
        raise NotImplementedError()

    @property
    def for_index(self):
        raise NotImplementedError()


class InputVertex(AlgObject, GraphScalar):
    def __init__(self,
                 internal_id: str,
                 id_value: ObjectProperty,
                 identifier_stem: ObjectProperty,
                 vertex_type: str,
                 vertex_properties: List[ObjectProperty] = None):
        super().__init__(internal_id, vertex_type, id_value, identifier_stem, vertex_properties)
        self._id_value = id_value

    @classmethod
    def parse_json(cls, json_dict: Dict):
        return cls(
            json_dict['internal_id'], json_dict['id_value'], json_dict['identifier_stem'],
            json_dict['vertex_type'], json_dict['vertex_properties']
        )

    @classmethod
    def from_arguments(cls, arguments):
        property_data = arguments.get('vertex_properties', {})
        vertex_properties = _parse_scalar_property_data(property_data)
        id_value_data = arguments['id_value']
        identifier_stem_data = arguments['identifier_stem']
        identifier_stem = ObjectProperty(
            'identifier_stem', LocalPropertyValue(
                identifier_stem_data['property_value'], identifier_stem_data['data_type'])
        )
        id_value = ObjectProperty(
            'id_value', LocalPropertyValue(id_value_data['property_value'], id_value_data['data_type'])
        )
        return cls(
            arguments['internal_id'], id_value, identifier_stem,
            arguments['vertex_type'], vertex_properties)

    @property
    def vertex_type(self):
        return self.object_type

    @property
    def vertex_properties(self):
        return self.object_properties

    @property
    def object_class(self):
        return 'Vertex'

    @property
    def for_index(self):
        index_value = self._for_index
        if self.numeric_id_value:
            index_value['numeric_id_value'] = self.numeric_id_value
        return index_value

    @property
    def numeric_id_value(self):
        try:
            return Decimal(self._id_value.property_value)
        except TypeError:
            return None


class InputEdge(AlgObject, GraphScalar):
    def __init__(self,
                 internal_id: str,
                 edge_label: str,
                 source_vertex_internal_id: str,
                 target_vertex_internal_id: str,
                 edge_properties: List[ObjectProperty] = None):
        edge_id_value = ObjectProperty('id_value', LocalPropertyValue(internal_id, 'S'))
        identifier_stem_value = f'#edge#{edge_label}'
        identifier_stem = ObjectProperty('identifier_stem', LocalPropertyValue(identifier_stem_value, 'S'))
        super().__init__(internal_id, edge_label, edge_id_value, identifier_stem, edge_properties)
        self._source_vertex_internal_id = source_vertex_internal_id
        self._target_vertex_internal_id = target_vertex_internal_id

    @classmethod
    def parse_json(cls, json_dict: Dict):
        edge_properties = json_dict.get('edge_properties', [])
        return cls(
            json_dict['internal_id'], json_dict['edge_label'],
            json_dict['source_vertex_internal_id'], json_dict['target_vertex_internal_id'],
            [ObjectProperty.from_json(x) for x in edge_properties]
        )

    @classmethod
    def from_arguments(cls, arguments):
        property_data = arguments.get('edge_properties', {})
        edge_properties = _parse_scalar_property_data(property_data)
        return cls(
            arguments['internal_id'], arguments['edge_label'],
            arguments['source_vertex_internal_id'], arguments['target_vertex_internal_id'], edge_properties)

    @property
    def edge_label(self):
        return self.object_type

    @property
    def edge_properties(self):
        return self.object_properties

    @property
    def source_vertex_internal_id(self):
        return self._source_vertex_internal_id

    @property
    def target_vertex_internal_id(self):
        return self._target_vertex_internal_id

    @property
    def object_class(self):
        return 'Edge'

    @property
    def for_index(self):
        index_value = self._for_index
        index_value.update({
            'from_internal_id': self._source_vertex_internal_id,
            'to_internal_id': self._target_vertex_internal_id,
        })
        return index_value


def _set_property_value_data_type(property_value: str, data_type: str) -> Union[str, Decimal]:
    accepted_data_types = ('S', 'N', 'B', 'DT')
    if data_type == 'S':
        return str(property_value)
    if data_type == 'N':
        return Decimal(property_value)
    if data_type == 'B':
        if property_value not in ['true', 'false']:
            raise RuntimeError(f'data provided for property value: {property_value}, '
                               f'is not acceptable boolean. accepted are: true, false literally')
        return property_value
    if data_type == 'DT':
        test_datetime = dateutil.parser.parse(property_value)
        return test_datetime.isoformat()
    raise NotImplementedError(f'attempted to create ObjectPropertyValue with data_type: {data_type}, '
                              f'accepted types are: {accepted_data_types}')


def _update_sensitive_data(source_internal_id: str,
                           property_name: str,
                           sensitive_value: str,
                           sensitive_table_name: str = None) -> str:
    """Push a sensitive value to remote storage

            Args:
                source_internal_id:
                property_name:
                sensitive_value:
                sensitive_table_name:

            Returns: The opaque pointer generated for the sensitive value

            Raises:
                ClientError: the update operation could not take place
                SensitiveValueAlreadyStored: the sensitive value has already been stored in the data space

            """
    if not sensitive_table_name:
        import os
        sensitive_table_name = os.environ['SENSITIVES_TABLE_NAME']
    logging.info(f'starting an update_sensitive_data function: {source_internal_id}, {property_name}')
    resource = boto3.resource('dynamodb')
    table = resource.Table(sensitive_table_name)
    logging.info(f'starting to create the sensitive pointer: {source_internal_id}, {property_name}')
    insensitive_value = _create_sensitive_pointer(property_name, source_internal_id)
    logging.info(f'created the sensitive pointer: {source_internal_id}, {property_name}, {insensitive_value}')
    try:
        table.update_item(
            Key={'insensitive': insensitive_value},
            UpdateExpression='SET sensitive_entry = if_not_exists(sensitive_entry, :s)',
            ExpressionAttributeValues={':s': sensitive_value},
            ReturnValues='NONE'
        )
        return insensitive_value
    except ClientError as e:
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise SensitiveValueAlreadyStored(property_name, source_internal_id, insensitive_value)
        logging.error(f'failed to update a sensitive data entry: {e}')
        raise e


def _create_sensitive_pointer(property_name: str, source_internal_id: str) -> str:
    pointer_string = ''.join([property_name, source_internal_id])
    return hashlib.sha3_512(pointer_string.encode('utf-8')).hexdigest()


def _parse_scalar_property_data(property_data: Dict) -> List[ObjectProperty]:
    parsed_properties = []
    local_properties = property_data.get('local_properties', [])
    sensitive_properties = property_data.get('sensitive_properties', [])
    stored_properties = property_data.get('stored_properties', [])
    for entry in local_properties:
        property_name = entry['property_name']
        property_value = LocalPropertyValue(entry['property_value'], entry['data_type'])
        parsed_properties.append(ObjectProperty(property_name, property_value))
    for entry in sensitive_properties:
        property_name = entry['property_name']
        sensitive_args = (entry['source_internal_id'], property_name, entry['property_value'], entry['data_type'])
        property_value = SensitivePropertyValue.generate_from_raw(*sensitive_args)
        parsed_properties.append(ObjectProperty(property_name, property_value))
    for entry in stored_properties:
        property_name = entry['property_name']
        property_value = StoredPropertyValue(entry['storage_uri'], entry['storage_class'], entry['data_type'])
        parsed_properties.append(ObjectProperty(property_name, property_value))
    return parsed_properties
