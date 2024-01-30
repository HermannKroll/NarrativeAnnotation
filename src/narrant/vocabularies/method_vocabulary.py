from narrant.config import METHOD_CLASSIFICATION_FILE, METHOD_TAGGER_VOCAB_DIRECTORY
from narrant.entitylinking.enttypes import LAB_METHOD, METHOD
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class MethodVocabulary:

    @staticmethod
    def read_method_classification(file=METHOD_CLASSIFICATION_FILE):
        desc2class = {}
        with open(file, 'rt') as f:
            for line in f:
                comps = line.strip().split('\t')
                if len(comps) == 2 and comps[0] == 'l':
                    desc2class[comps[1]] = LAB_METHOD
                elif len(comps) == 2 and comps[0] == 'unspezif.':
                    desc2class[comps[1]] = None
                else:
                    desc2class[comps[0]] = METHOD
        return desc2class

    @staticmethod
    def enhance_methods_by_rules(term2desc: {str: str}):
        term2desc_copy = term2desc.copy()
        for term, descs in term2desc.items():
            if 'metric' in term:
                term2desc_copy[term.replace('metric', 'metry')] = descs
            if 'metry' in term:
                term2desc_copy[term.replace('metry', 'metric')] = descs
            if 'stain' in term and not 'staining' in term:
                term2desc_copy[term.replace('stain', 'staining')] = descs
            if 'staining' in term:
                term2desc_copy[term.replace('staining', 'stain')] = descs

        return term2desc_copy

    @staticmethod
    def create_method_vocabulary(expand_terms=True, method_type=METHOD):
        term2desc = GenericVocabulary.create_vocabulary_from_directory(METHOD_TAGGER_VOCAB_DIRECTORY,
                                                                       expand_terms=expand_terms)
        term2desc = MethodVocabulary.enhance_methods_by_rules(term2desc)
        desc2class = MethodVocabulary.read_method_classification()
        missing_classes = set()
        for k, descs in term2desc.items():
            for d in descs:
                if d not in desc2class:
                    missing_classes.add(d)
        if len(missing_classes) > 0:
            raise ValueError(
                f'The following descriptors must be classified in {METHOD_CLASSIFICATION_FILE}: {missing_classes}')

        term2methods = {k: list([d for d in descs if desc2class[d] == method_type]) for k, descs in term2desc.items()}
        return {k: v for k, v in term2methods.items() if v and len(v) > 0}
