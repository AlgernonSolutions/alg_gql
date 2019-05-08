import logging
import os
from typing import Union, Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from algernon import ajson

from toll_booth.obj.graph.gql_scalars import InputEdge, InputVertex
from toll_booth.obj.index.indexes import UniqueIndex
from toll_booth.obj.index.troubles import MissingIndexedPropertyException, UniqueIndexViolationException


class IndexManager:
    """Reads and writes values to the index

        the index manager interacts with the DynamoDB table to add and read indexed entries
    """
    def __init__(self, table_name: str = None):
        """

        Args:
            table_name:
        """
        if table_name is None:
            table_name = os.environ['INDEX_TABLE_NAME']
        object_index = UniqueIndex.for_object_index()
        internal_id_index = UniqueIndex.for_internal_id_index()
        identifier_stem_index = UniqueIndex.for_identifier_stem_index()
        indexes = [object_index, internal_id_index, identifier_stem_index]
        self._table_name = table_name
        self._object_index = object_index
        self._internal_id_index = internal_id_index
        self._identifier_stem_index = identifier_stem_index
        self._table = boto3.resource('dynamodb').Table(self._table_name)
        self._indexes = indexes

    def index_object(self, scalar_object: Union[InputEdge, InputVertex]):
        """

        Args:
            scalar_object:

        Returns: nothing

        Raises:
            AttemptedStubIndexException: The object being indexed is missing key identifying information
            MissingIndexedPropertyException: The object was complete, but it does not have one or more properties
                specified by the index

        """
        for index in self._indexes:
            if index.check_object_type(scalar_object.object_type):
                missing_properties = index.check_for_missing_object_properties(scalar_object)
                if missing_properties:
                    raise MissingIndexedPropertyException(index.index_name, index.indexed_fields, missing_properties)
        return self._index_object(scalar_object)

    def find_potential_vertexes(self, object_type: str, vertex_properties: Dict) -> [Dict]:
        """checks the index for objects that match on the given object type and vertex properties

        Args:
            object_type: the type of the object
            vertex_properties: a dictionary containing the properties to check for in the index

        Returns:
            a list of all the potential vertexes that were found in the index

        """
        potential_vertexes, token = self._scan_vertexes(object_type, vertex_properties)
        while token:
            more_vertexes, token = self._scan_vertexes(object_type, vertex_properties, token)
            potential_vertexes.extend(more_vertexes)
        logging.info('completed a scan of the data space to find potential vertexes with properties: %s '
                     'returned the raw values of: %s' % (vertex_properties, potential_vertexes))
        return [x for x in potential_vertexes]

    def get_object(self, internal_id: str):
        response = self._table.query(
            IndexName=self._internal_id_index.index_name,
            KeyConditionExpression=Key('internal_id').eq(internal_id)
        )
        if response['Count'] > 1:
            raise RuntimeError(f'internal_id value: {internal_id} has some how been indexed multiple times, '
                               f'big problem: {response["Items"]}')
        for entry in response['Items']:
            return entry['object_value']

    def delete_object(self, internal_id: str):
        existing_object = self.get_object(internal_id)
        if existing_object:
            indexed_object = ajson.loads(self.get_object(internal_id))
            identifier_stem, sid_value = indexed_object['identifier_stem'], indexed_object['sid_value']
            self._table.delete_item(Key={'sid_value': sid_value, 'identifier_stem': identifier_stem})

    def _index_object(self, scalar_object: Union[InputVertex, InputEdge]):
        """Adds an object to the index per the schema

        Args:
            scalar_object:

        Returns: None

        Raises:
            UniqueIndexViolationException: The object to be graphed is already in the index

        """
        item = scalar_object.for_index
        try:
            item.update({
                'from_internal_id': scalar_object.source_vertex_internal_id,
                'to_internal_id': scalar_object.target_vertex_internal_id,
                'object_class': 'Edge'
            })
        except AttributeError:
            item['object_class'] = 'Vertex'
        args = {
            'Item': item,
            'ReturnValues': 'ALL_OLD',
            'ReturnConsumedCapacity': 'INDEXES',
            'ReturnItemCollectionMetrics': 'SIZE'

        }
        condition_expressions = set()
        unique_index_names = []
        for index in self._indexes:
            if index.is_unique:
                condition_expressions.update(index.conditional_statement)
                unique_index_names.append(index.index_name)
        if condition_expressions:
            args['ConditionExpression'] = ' AND '.join(condition_expressions)
        try:
            results = self._table.put_item(**args)
            return results
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise e
            raise UniqueIndexViolationException(', '.join(unique_index_names), item)

    def _scan_vertexes(self, object_type: str, vertex_properties: dict, token: str = None) -> (list, Union[str, None]):
        """conducts a single paginated scan of the index space

        Args:
            object_type: the type of the object being scanned for
            vertex_properties: a dict containing the vertex properties to check for
            token: if running a subsequent scan, the token from the last scan

        Returns:
            a tuple containing a list of the items found in the index, and the pagination token if present
        """
        filter_properties = [f'(begins_with(identifier_stem, :is) OR begins_with(identifier_stem, :stub))']
        expression_names = {}
        expression_values = {
            ':is': f'#vertex#{object_type}#',
            ':stub': '#vertex#stub#',
        }
        pointer = 1
        for property_name, vertex_property in vertex_properties.items():
            if hasattr(vertex_property, 'is_missing'):
                continue
            filter_properties.append(f'object_properties.#{pointer} = :property{pointer}')
            expression_names[f'#{pointer}'] = property_name
            expression_values[f':property{pointer}'] = vertex_property
            pointer += 1
        scan_kwargs = {
            'FilterExpression': ' AND '.join(filter_properties),
            'ExpressionAttributeNames': expression_names,
            'ExpressionAttributeValues': expression_values
        }
        if token:
            scan_kwargs['ExclusiveStartKey'] = token
        results = self._table.scan(**scan_kwargs)
        return results['Items'], results.get('LastEvaluatedKey', None)
