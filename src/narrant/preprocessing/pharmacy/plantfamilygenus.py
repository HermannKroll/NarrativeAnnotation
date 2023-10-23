from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.entitylinking.classifier import Classifier
from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.plant_family_genus import PlantFamilyGenusVocabulary


class PlantFamilyGenusTagger(IndexedDictTagger):
    TYPES = (enttypes.PLANT_FAMILY_GENUS,)
    __name__ = "PlantFamilyTagger"
    __version__ = "2.0.0"
    PLANT_CLASSIFICATION = "PlantSpecific"

    def __init__(self, *args, **kwargs):
        super().__init__("plantfamily", "PlantFamilyTagger", PlantFamilyGenusTagger.__version__,
                         enttypes.PLANT_FAMILY_GENUS, config.PLANT_GENUS_DATABASE_FILE,
                         *args, **kwargs)

        self.classifier = Classifier(PlantFamilyGenusTagger.PLANT_CLASSIFICATION, config.PLANT_SPECIFIC_RULES)
        self.plant_families = PlantFamilyGenusVocabulary.read_wikidata_plant_families()

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = PlantFamilyGenusVocabulary.read_plant_family_genus_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} Plant Families found in database')

    def keep_entity_tags(self, in_doc: TaggedDocument) -> bool:
        self.classifier.classify_document(in_doc)
        # Either it does contain a plant family (not only a genus)
        classified_plants = {p.ent_id for p in in_doc.tags if p.ent_type == enttypes.PLANT_FAMILY_GENUS}
        if len(classified_plants.intersection(self.plant_families)) > 0:
            return True
        # Or it is plant specific classified
        if PlantFamilyGenusTagger.PLANT_CLASSIFICATION in in_doc.classification:
            return True
        return False

    def custom_tag_filter_logic(self, in_doc: TaggedDocument):
        plant_tags = list([t for t in in_doc.tags if t.ent_type == enttypes.PLANT_FAMILY_GENUS])
        if len(plant_tags) > 0:
            if not self.keep_entity_tags(in_doc):
                # remove all plant family tags
                in_doc.tags = list([t for t in in_doc.tags if t.ent_type != enttypes.PLANT_FAMILY_GENUS])
