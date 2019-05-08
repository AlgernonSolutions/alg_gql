import importlib
import json
from decimal import Decimal


class GqlDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj):
        if '_alg_class' not in obj:
            return obj
        alg_class = obj['_alg_class']
        obj_value = obj['value']
        if alg_class == 'frozenset':
            return frozenset(x for x in obj_value)
        if alg_class == 'tuple':
            return tuple(x for x in obj_value)
        if alg_class == 'datetime':
            return str(obj_value)
        if alg_class == 'decimal':
            return Decimal(obj_value)
        if '_alg_module' not in obj:
            return obj
        alg_module = obj['_alg_module']
        host_module = importlib.import_module(alg_module)
        obj_class = getattr(host_module, alg_class, None)
        if obj_class is None:
            return obj
        alg_obj = obj_class.from_json(obj_value)
        return alg_obj.to_gql
