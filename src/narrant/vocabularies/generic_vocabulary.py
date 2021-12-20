import logging
import os
from abc import ABCMeta

from narrant.preprocessing.tagging.vocabulary import Vocabulary
from narrant.vocabularies.mesh_vocabulary import MeSHVocabulary


class GenericVocabulary(ABCMeta):

    @staticmethod
    def load_additional_mesh_descriptors(file):
        additional_descriptors = set()
        with open(file, 'rt') as f:
            for line in f:
                line = line.strip()
                if 'D' not in line:
                    raise ValueError(f'MeSH Descriptor must start with a D: {line}')

                if line.startswith('MESH'):
                    line = line.replace('MESH:', '')

                additional_descriptors.add(line)
        return additional_descriptors

    @staticmethod
    def merge_vocab_into_1(vocab1, vocab2):
        for term, ids in vocab2.items():
            if term in vocab1:
                vocab1[term].update(ids)
            else:
                vocab1[term] = ids

    @staticmethod
    def create_vocabulary_from_directory(vocab_dir: str, expand_terms=True):
        desc_by_term = {}
        # Is a MeSH tree file included? then build the vocabulary from these subtrees
        mesh_tree_file = os.path.join(vocab_dir, "mesh_tree_numbers.txt")
        if os.path.isfile(mesh_tree_file):
            tree_numbers = set()
            with open(mesh_tree_file, 'rt') as f:
                for line in f:
                    tree_numbers.add(line.strip())
            logging.info(f'Creating vocabulary from MeSH tree numbers: {tree_numbers}')
            desc_by_term = MeSHVocabulary.create_mesh_vocab(list(tree_numbers), expand_terms=expand_terms)

        # is a entity vocabulary file included?
        vocabulary_file = os.path.join(vocab_dir, 'vocabulary.tsv')
        if os.path.isfile(vocabulary_file):
            vocab = Vocabulary(vocabulary_file)
            vocab.load_vocab(expand_terms=expand_terms)
            for ent_type in vocab.get_ent_types():
                logging.info(f'Entity vocabulary loaded. {len(vocab.vocabularies[ent_type])} terms found for: {ent_type}')
                GenericVocabulary.merge_vocab_into_1(desc_by_term, vocab.vocabularies[ent_type])

        add_mesh_desc_file = os.path.join(vocab_dir, 'mesh_descriptors.txt')
        if os.path.isfile(add_mesh_desc_file):
            additional_mesh_descriptors = GenericVocabulary.load_additional_mesh_descriptors(add_mesh_desc_file)
            logging.info(f'{len(additional_mesh_descriptors)} additional MeSH descriptors load from file...')
            add_mesh_vocab = MeSHVocabulary.create_mesh_vocab_from_desc(additional_mesh_descriptors)
            logging.info(f'{len(add_mesh_vocab)} additional terms retrieved from MeSH')
            GenericVocabulary.merge_vocab_into_1(desc_by_term, add_mesh_vocab)

        return desc_by_term
