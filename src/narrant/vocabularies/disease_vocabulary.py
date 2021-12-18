from narrant.config import MESH_DESCRIPTORS_FILE
from narrant.vocabularies.mesh_vocabulary import MeSHVocabulary


class DiseaseVocabulary:

    @staticmethod
    def create_disease_vocabulary(mesh_file=MESH_DESCRIPTORS_FILE, expand_by_s_and_e=True):
        return MeSHVocabulary.create_mesh_vocab(['C', 'F03'], mesh_file, expand_by_s_and_e)