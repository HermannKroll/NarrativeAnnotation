import logging
from collections import defaultdict
from typing import List

from narrant.config import MESH_DESCRIPTORS_FILE
from narrant.mesh.data import MeSHDB
from narrant.preprocessing.tagging.vocabulary import expand_vocabulary_term


class MeSHVocabulary:

    @staticmethod
    def create_mesh_vocab(subtrees: List[str], mesh_file=MESH_DESCRIPTORS_FILE, expand_terms=True):
        desc_by_term = defaultdict(set)

        meshdb = MeSHDB.instance()
        meshdb.load_xml(mesh_file)
        logging.info('Extracting MeSH information (terms) ...')
        for desc in meshdb.get_all_descs():
            has_correct_tree = False
            # check if a descriptor's tree matches the allowed subtrees
            for tn in desc.tree_numbers:
                for allowed_tree in subtrees:
                    if tn.startswith(allowed_tree):
                        has_correct_tree = True
            # ignore descriptor
            if not has_correct_tree:
                continue

            mesh_desc = f'MESH:{desc.unique_id}'
            if expand_terms:
                for t_e in expand_vocabulary_term(desc.name.lower().strip()):
                    desc_by_term[t_e].add(mesh_desc)
            else:
                desc_by_term[desc.name.lower().strip()].add(mesh_desc)
            for t in desc.terms:
                if expand_terms:
                    for t_e in expand_vocabulary_term(t.string.lower().strip()):
                        desc_by_term[t_e].add(mesh_desc)
                else:
                    desc_by_term[t.string.lower().strip()].add(mesh_desc)
        return desc_by_term