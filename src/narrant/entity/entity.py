def get_unique_entity_key(entity_type: str, entity_id: str) -> str:
    """
    Generates a unique entity key as a string
    :param entity_type: entity type
    :param entity_id: entity id
    :return: unique entity key
    """
    return '___'.join([entity_type, entity_id])


class Entity:

    def __init__(self, entity_id, entity_type, entity_name=None, entity_class=None):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.entity_class = entity_class

    def __hash__(self):
        return hash(self.get_unique_key())

    def __eq__(self, other):
        return other.entity_id == self.entity_id and other.entity_type == self.entity_type

    def __str__(self):
        return '{} ({})'.format(self.entity_id, self.entity_type)

    def __repr__(self):
        return '{} ({})'.format(self.entity_id, self.entity_type)

    def to_dict(self):
        return dict(entity_id=self.entity_id, entity_type=self.entity_type, entity_name=self.entity_name)

    def get_unique_key(self):
        return get_unique_entity_key(entity_type=self.entity_type, entity_id=self.entity_id)
