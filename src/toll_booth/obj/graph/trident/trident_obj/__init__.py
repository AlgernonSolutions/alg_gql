from typing import List, Dict, Any

import rapidjson


def _parse_property_value(property_attributes: List[Any]) -> Dict[str, Any]:
    if len(property_attributes) > 2:
        raise RuntimeError(f'received property attributes: {property_attributes}, '
                           f'but there are too many, should be two')
    for property_attribute in property_attributes:
        try:
            return rapidjson.loads(property_attribute)
        except (ValueError, TypeError):
            continue
    raise NotImplementedError(f'could not parse trident property for property_attributes: {property_attributes}')


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
