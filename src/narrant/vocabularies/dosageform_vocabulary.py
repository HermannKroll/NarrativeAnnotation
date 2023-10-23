import re
from collections import defaultdict

from kgextractiontoolbox.entitylinking.tagging.vocabulary import expand_vocabulary_term
from narrant.config import DOSAGEFORM_TAGGER_VOCAB_DIRECTORY
from narrant.vocabularies.generic_vocabulary import GenericVocabulary


class DosageFormVocabulary:

    @staticmethod
    def create_dosage_form_vocabulary(expand_by_s_and_e=True):
        desc_by_term = GenericVocabulary.create_vocabulary_from_directory(DOSAGEFORM_TAGGER_VOCAB_DIRECTORY,
                                                                          expand_terms=expand_by_s_and_e)

        # expand all terms by our rules
        regex_micro = re.compile(r'micro[a-z]')
        regex_intra = re.compile(r'intra[a-z]')
        regex_nano = re.compile(r'nano[a-z]')
        expanded_terms = defaultdict(set)
        for term, descs in desc_by_term.items():
            new_terms = []
            if regex_micro.match(term):
                t1 = term.replace('micro', 'micro ')
                t2 = term.replace('micro', 'micro-')
                new_terms.append(t1)
                new_terms.append(t2)
            if regex_intra.match(term):
                t1 = term.replace('intra', 'intra ')
                t2 = term.replace('intra', 'intra-')
                new_terms.append(t1)
                new_terms.append(t2)
            if regex_nano.match(term):
                t1 = term.replace('nano', 'nano ')
                t2 = term.replace('nano', 'nano-')
                new_terms.append(t1)
                new_terms.append(t2)

            for t in new_terms:
                if expand_by_s_and_e:
                    for e_t in expand_vocabulary_term(t):
                        expanded_terms[e_t].update(descs)
                else:
                    expanded_terms[t].update(descs)

        GenericVocabulary.merge_vocab_into_1(desc_by_term, expanded_terms)
        return desc_by_term
