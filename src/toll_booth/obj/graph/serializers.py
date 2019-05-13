import importlib
import json
import logging
from decimal import Decimal


class GqlDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj):
        logging.info(f'starting a GQL Decoding operation for: {obj}')
        if '_alg_class' not in obj:
            logging.info(f'object is not an algernon object, let the default handle it')
            return obj
        alg_class = obj['_alg_class']
        obj_value = obj['value']
        logging.info(f'object is an algernon object, class: {alg_class}, value: {obj_value}')
        if alg_class == 'frozenset':
            return frozenset(x for x in obj_value)
        if alg_class == 'tuple':
            return tuple(x for x in obj_value)
        if alg_class == 'datetime':
            return str(obj_value)
        if alg_class == 'decimal':
            return Decimal(obj_value)
        if '_alg_module' not in obj:
            logging.info(f'_alg_module not found in {obj_value} for {alg_class}, possibly error brewing')
            return obj
        alg_module = obj['_alg_module']
        logging.info(f'alg_module for {obj_value} for {alg_class} is {alg_module}')
        host_module = importlib.import_module(alg_module)
        obj_class = getattr(host_module, alg_class, None)
        if obj_class is None:
            logging.warning(f'could not find obj_class for {obj_value} of {alg_module}.{alg_class}')
            return obj
        alg_obj = obj_class.from_json(obj_value)
        logging.info(f'after remake, {alg_module}.{alg_class} is {alg_obj}')
        alg_gql = alg_obj.to_gql
        logging.info(f'gql variant of {alg_obj} is {alg_gql}')
        return alg_gql
