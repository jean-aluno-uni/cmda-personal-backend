from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Payloads de entrada/saída da API em camelCase (convenção comum de REST APIs
    consumidas por clientes JS/Dart), mantendo o código Python em snake_case."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
