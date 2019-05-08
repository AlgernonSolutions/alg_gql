class InvalidGqlRequestException(Exception):
    def __init__(self, query_type, field_name, missing_fields):
        self._query_type = query_type
        self._field_name = field_name
        self._missing_fields = missing_fields
        msg = f'tried to execute {query_type}.{field_name} but missing required argument {", ".join(missing_fields)}'
        super().__init__(msg)
