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
        if entity_type == GENE:
            try:
                return self.generesolver.gene_id_to_symbol(entity_id).lower()
            except (KeyError, ValueError):
                print("Error at translating a gene ID to a gene Symbol.")
        else:
            return entity_id
