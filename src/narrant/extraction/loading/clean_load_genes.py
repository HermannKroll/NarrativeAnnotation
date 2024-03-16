import logging
from collections import namedtuple
from datetime import datetime
from typing import List

from kgextractiontoolbox.progress import print_progress_with_eta
from narrant.entity.entityidtranslator import EntityIDTranslator
from narrant.entitylinking.enttypes import GENE

PRED = namedtuple('Predication', ['doc_id', 'subj', 'pred', 'pred_cleaned', 'obj', 'conf', 'sent', 's_id', 's_str',
                                  's_type', 'o_id', 'o_str', 'o_type'])


def clean_and_translate_gene_ids(predications: List[PRED]):
    """
     Gene IDs are unique for each species - We are only interested in the names of genes
     Thus, we map each gene id to its gene symbol, so that, e.g. CYP3A4 is the unique description for all species
     :param predications: a list of predications
     :return: a list of cleaned predications
     """
    logging.info('Cleaning and translating gene ids...')
    predications_cleaned = []
    entityidtranslator = EntityIDTranslator()
    start_time = datetime.now()
    predications_len = len(predications)
    for idx, p in enumerate(predications):
        try:
            subj_id = entityidtranslator.translate_entity_id(p.s_id, GENE)
            obj_id = entityidtranslator.translate_entity_id(p.o_id, GENE)
            p_cleaned = PRED(p.doc_id, p.subj, p.pred, p.pred_cleaned, p.obj, p.conf, p.sent, subj_id, p.s_str, p.s_type,
                             obj_id, p.o_str, p.o_type)
            predications_cleaned.append(p_cleaned)
        except (KeyError, ValueError):
            pass
        print_progress_with_eta('cleaning gene ids...', idx, predications_len, start_time)
    logging.info('{} predications obtained'.format(len(predications_cleaned)))
    return predications_cleaned
