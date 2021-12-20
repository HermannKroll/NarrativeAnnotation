import logging
from itertools import islice

import narrant.vocabularies.drug_vocabulary as drug_vocab
from narrant import config
from narrant.preprocessing.tagging.dictagger import clean_vocab_word_by_split_rules
from narrant.preprocessing.tagging.vocabulary import expand_vocabulary_term


class ExcipientVocabulary:

    @staticmethod
    def _parse_single_excipient_per_line_file(filepath: str, expand_terms) -> {str: [str]}:
        excipient_dict = {}
        with open(filepath, 'rt') as f:
            for line in f:
                excipient = line.lower().strip()
                excipient_heading = excipient.capitalize()
                if expand_terms:
                    excipient_terms = expand_vocabulary_term(excipient)
                else:
                    excipient_terms = [excipient]
                for term in excipient_terms:
                    if term in excipient_dict:
                        excipient_dict[term].add(excipient_heading)
                    else:
                        excipient_dict[term] = {excipient_heading}
        return excipient_dict

    @staticmethod
    def read_excipients_names(source_file=config.EXCIPIENT_TAGGER_DATABASE_FILE,
                              excipients_curated_file=config.EXCIPIENT_CURATED_LIST_FILE,
                              drugbank_excipient_file=config.EXCIPIENT_TAGGER_DRUGBANK_EXCIPIENT_FILE,
                              expand_terms=True):
        excipient_dict = {}
        with open(source_file, 'rt') as f:
            for line in islice(f, 1, None):
                comps = line.split('~')
                excipient = clean_vocab_word_by_split_rules(comps[0].strip().lower())
                excipient_heading = excipient.capitalize()
                if expand_terms:
                    excipient_terms = expand_vocabulary_term(excipient)
                else:
                    excipient_terms = [excipient]
                for term in excipient_terms:
                    if term in excipient_dict:
                        excipient_dict[term].add(excipient_heading)
                    else:
                        excipient_dict[term] = {excipient_heading}

        excipient_dict.update(ExcipientVocabulary._parse_single_excipient_per_line_file(drugbank_excipient_file,
                                                                                        expand_terms=expand_terms))

        excipient_dict.update(ExcipientVocabulary._parse_single_excipient_per_line_file(excipients_curated_file,
                                                                                        expand_terms=expand_terms))

        return excipient_dict

    @staticmethod
    def create_excipient_vocabulary(excipient_database=config.EXCIPIENT_TAGGER_DATABASE_FILE,
                                    chembl_db_file=config.CHEMBL_DRUG_CSV, ):
        # we cannot ignore the excipient terms while reading chembl here (else our mapping would be empty)
        chembl_terms = drug_vocab.DrugVocabulary.create_drug_vocabulary_from_chembl(source_file=chembl_db_file,
                                                                                    ignore_excipient_terms=False,
                                                                                    ignore_drugbank_chemicals=False)
        logging.info(f'Reading excipient database: {excipient_database}...')
        excipient_terms = ExcipientVocabulary.read_excipients_names()
        chembl_identifiers_for_excipients = set()
        desc_by_term = {}
        # extend dict by all excipient terms
        # if an excipient term is found in chembl - use the chembl identifier for tagging
        for excipient_term, excipient_headings in excipient_terms.items():
            # do we find a corresponding term in drugbank
            if excipient_term in chembl_terms:
                # yes - we take the DrugBank identifier
                chembl_identifiers_for_excipients.update(chembl_terms[excipient_term])
            else:
                desc_by_term[excipient_term] = excipient_headings

        # search all chembl terms which map to excipient chembl identifier
        for chembl_term, chids in chembl_terms.items():
            for chid in chids:
                if chid in chembl_identifiers_for_excipients:
                    # the chembl term will be mapped to its corresponding dbid
                    desc_by_term[chembl_term] = chids
                    # stop iteration here
                    break

        return desc_by_term
