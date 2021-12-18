from narrant.config import MESH_DESCRIPTORS_FILE
from narrant.preprocessing.enttypes import LAB_METHOD
from narrant.vocabularies.method_vocabulary import MethodVocabulary


class LabMethodVocabulary:

    @staticmethod
    def create_lab_method_vocabulary(mesh_file=MESH_DESCRIPTORS_FILE, expand_terms=True):
        term2desc = MethodVocabulary.create_method_vocabulary(mesh_file, expand_terms=expand_terms,
                                                              method_type=LAB_METHOD)
        if 'assay' not in term2desc:
            term2desc['assay'] = ['FIDXLM1']
        else:
            term2desc['assay'].append('FIDXLM1')
        return term2desc