import argparse
import logging

from narrant.config import METHOD_TAGGER_VOCAB_DIRECTORY
from narrant.entity.entityresolver import EntityResolver
from narrant.preprocessing.enttypes import LAB_METHOD
from narrant.vocabularies.generic_vocabulary import GenericVocabulary
from narrant.vocabularies.method_vocabulary import MethodVocabulary


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    term2desc = GenericVocabulary.create_vocabulary_from_directory(METHOD_TAGGER_VOCAB_DIRECTORY,
                                                                   expand_terms=False)
    term2desc = MethodVocabulary.enhance_methods_by_rules(term2desc)
    desc2class = MethodVocabulary.read_method_classification()
    missing_classes = set()
    for k, descs in term2desc.items():
        for d in descs:
            if d not in desc2class:
                missing_classes.add(d)

    resolver = EntityResolver.instance()

    print('--' *60)
    print('Not classified methods:')
    print('--' *60)
    for ms in missing_classes:
        print(f'{ms}\t{resolver.get_name_for_var_ent_id(ms, LAB_METHOD)}')

    print('--' *60)



if __name__ == "__main__":
    main()
