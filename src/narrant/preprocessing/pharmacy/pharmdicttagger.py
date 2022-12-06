import logging
from typing import Dict

from narrant.preprocessing import enttypes as et
from narrant.preprocessing.pharmacy import chemical, drug, method, labmethod, excipient, plantfamilygenus, disease, \
    dosage, vaccine, healthstatus
from narrant.preprocessing.tagging import indexed_dictagger as dt
from kgextractiontoolbox.entitylinking.tagging.metadictagger import MetaDicTagger


class PharmDictTagger:
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
        et.HEALTH_STATUS: healthstatus.HealthStatusTagger
    }

    @staticmethod
    def get_supported_tagtypes():
        return set(PharmDictTagger.tagger_by_type.keys())

    def __init__(self, tag_types, tagger_kwargs):
        self.tag_types = tag_types
        self.tagger_kwargs = tagger_kwargs

    def create_MetaDicTagger(self):
        metatag = MetaDicTagger(**self.tagger_kwargs)
        for tag_type in self.tag_types:
            subtagger = PharmDictTagger.tagger_by_type.get(tag_type)
            if not subtagger:
                logging.warning(f"No tagging class found for tagtype {tag_type}!")
                continue
            metatag.add_tagger(subtagger(**self.tagger_kwargs))

        # reset taggers name and version
        metatag.__name__ = self.__name__
        metatag.__version__ = self.__version__
        return metatag
