from narrant.entity.entityresolver import GeneResolver
from narrant.entitylinking.enttypes import GENE


class EntityIDTranslator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.generesolver = GeneResolver()
            cls._instance.generesolver.load_index()
        return cls._instance

    def translate_entity_id(self, entity_id, entity_type):
        """
        Translates a gene ids - > may throw an key error or value errror
        :param entity_id:
        :param entity_type:
        :return:
        """
        if entity_type == GENE:
            return self.generesolver.gene_id_to_symbol(entity_id).lower()
        else:
            return entity_id
