import logging
from typing import Dict, List

from kgextractiontoolbox.document.document import TaggedEntity
from kgextractiontoolbox.entitylinking.tagging.dictagger import DictTagger
from kgextractiontoolbox.entitylinking.tagging.metadictagger import MetaDicTagger
from narrant.entitylinking import enttypes as et
from narrant.entitylinking.pharmacy import chemical, drug, method, labmethod, excipient, plantfamilygenus, disease, \
    dosage, vaccine, healthstatus, organism, tissue
from narrant.entitylinking.tagging import indexed_dictagger as dt


class PharmDictTagger(MetaDicTagger):
    __name__ = "PharmDictTagger"
    __version__ = "1.0"

    tagger_by_type: Dict[str, dt.IndexedDictTagger] = {
        et.DRUG: drug.DrugTagger,
        et.DOSAGE_FORM: dosage.DosageFormTagger,
        et.EXCIPIENT: excipient.ExcipientTagger,
        et.PLANT_FAMILY_GENUS: plantfamilygenus.PlantFamilyGenusTagger,
        et.CHEMBL_CHEMICAL: chemical.ChemicalTagger,
        et.DISEASE: disease.DiseaseTagger,
        et.METHOD: method.MethodTagger,
        et.LAB_METHOD: labmethod.LabMethodTagger,
        et.VACCINE: vaccine.VaccineTagger,
        et.HEALTH_STATUS: healthstatus.HealthStatusTagger,
        et.ORGANISM: organism.OrganismTagger,
        et.TISSUE: tissue.TissueTagger
    }

    ignored_tag_types_to_clean = {
        et.HEALTH_STATUS
    }

    @staticmethod
    def get_supported_tagtypes():
        return set(PharmDictTagger.tagger_by_type.keys())

    def __init__(self, tag_types, tagger_kwargs):
        super().__init__(**tagger_kwargs)
        self.tag_types = tag_types

        for tag_type in self.tag_types:
            subtagger = PharmDictTagger.tagger_by_type.get(tag_type)
            if not subtagger:
                logging.warning(f"No tagging class found for tagtype {tag_type}!")
                continue
            super().add_tagger(subtagger(**tagger_kwargs))

        self.clean_abbreviation_tags_function = self.clean_abbreviation_tags_pharmacy

    def clean_abbreviation_tags_pharmacy(self, tags: List[TaggedEntity], minimum_tag_len: int):
        """
        This method sorts the tags by type and cleans up those that should have not an ignored type. This retains
        short but important tags, e.g. "men" with entity_type=HEALTH_STATUS.
        :param minimum_tag_len: the minimum tag length to treat a term as a 'full' tag
        :param tags: a list of tags
        :return: a list of cleaned tags
        """
        tags_ignored = list()
        tags_to_clean = list()
        for tag in tags:
            if tag.ent_type in self.ignored_tag_types_to_clean:
                tags_ignored.append(tag)
            else:
                tags_to_clean.append(tag)

        tags = DictTagger.clean_abbreviation_tags(tags_to_clean, minimum_tag_len)
        tags += tags_ignored
        return tags
