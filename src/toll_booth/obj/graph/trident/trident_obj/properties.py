from typing import Dict, Any

from algernon import AlgObject


class TridentProperty(AlgObject):
    def __init__(self, property_label: str, property_value: str):
        self._property_label = property_label
        self._property_value = property_value

    def __len__(self):
        return 1

    def __str__(self):
        return str(self._property_value)

    def __int__(self):
        return int(self._property_value)

    @classmethod
    def parse_json(cls, json_dict: Dict[str, Any]):
        return cls(
            json_dict['property_label'],
            json_dict['property_value']
        )

    @property
    def label(self):
        return self._property_label

    @property
    def value(self):
        return self._property_value
