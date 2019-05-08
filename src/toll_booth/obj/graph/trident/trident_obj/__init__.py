from typing import List, Dict, Any


def _parse_property_value(property_attributes: List[Any]) -> Dict[str, Any]:
    property_value = property_attributes[0]
    property_data_type = property_attributes[1]
    property_class = property_attributes[2]
    if property_class == 'SensitivePropertyValue':
        return {
            '__typename': property_class,
            'pointer': property_value,
            'data_type': property_data_type,
        }
    if property_class == 'LocalPropertyValue':
        return {
            '__typename': property_class,
            'property_value': property_value,
            'data_type': property_data_type,
        }
    if property_class == 'StoredPropertyValue':
        return {
            '__typename': property_class,
            'storage_uri': property_value,
            'data_type': property_data_type,
            'storage_class': property_attributes[3]
        }
    raise NotImplementedError(f'could not parse trident property for property_class: {property_class}')


def parse_object_properties(property_name: str, object_properties: List[Any]) -> Dict[str, Any]:
    property_attributes = []
    for object_property in object_properties:
        property_attributes.append(object_property['_property_value'])
    gql = {
        '__typename': 'ObjectProperty',
        'property_name': property_name,
        'property_value': _parse_property_value(property_attributes)
    }
    return gql
