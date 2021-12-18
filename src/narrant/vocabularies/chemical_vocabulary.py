import narrant.vocabularies.drug_vocabulary as drug_vocab
import narrant.vocabularies.excipient_vocabulary as exc_vocab

from narrant import config


class ChemicalVocabulary:

    @staticmethod
    def read_drugbank_chemical_names(drugbank_chemical_list=config.CHEMBL_CHEMICAL_DATABASE_FILE):
        chemical_mapping = {}
        with open(drugbank_chemical_list, 'rt') as f:
            for line in f:
                chemical = line.strip()
                chemical_mapping[chemical.lower()] = chemical.capitalize()
        return chemical_mapping

    @staticmethod
    def create_chembl_chemical_vocabulary(chemical_list=config.CHEMBL_CHEMICAL_DATABASE_FILE,
                                          chembl_db_file=config.CHEMBL_DRUG_CSV,
                                          excipient_db=config.EXCIPIENT_TAGGER_DATABASE_FILE):
        # we cannot ignore the excipient terms while reading Chembl here (else our mapping would be empty)
        drugbank_terms = drug_vocab.DrugVocabulary.create_drug_vocabulary_from_chembl(source_file=chembl_db_file,
                                                                                      ignore_excipient_terms=False,
                                                                                      ignore_drugbank_chemicals=False)
        # drugbank chemicals
        drugbank_chemicals_mapping = ChemicalVocabulary.read_drugbank_chemical_names(chemical_list)
        chembl_identifiers_for_chemical = set()
        desc_by_term = {}
        # if an chemical term is found in Chembl - use the Chembl identifier for tagging
        for chemical_term, chemical_heading in drugbank_chemicals_mapping.items():
            # do we find a corresponding term in Chembl
            if chemical_term in drugbank_terms:
                # yes - we take the DrugBank identifier
                chembl_identifiers_for_chemical.update(drugbank_terms[chemical_term])
            else:
                desc_by_term[chemical_term] = [chemical_heading]

        # search all chembl terms which map to a chemical Chembl identifier
        for chembl_term, chids in drugbank_terms.items():
            for chid in chids:
                if chid in chembl_identifiers_for_chemical:
                    # the drugbank term will be mapped to its corresponding dbid
                    desc_by_term[chembl_term] = chids
                    # stop iteration here
                    break

        # ignore all excipient terms
        excipient_by_term = exc_vocab.ExcipientVocabulary.create_excipient_vocabulary(excipient_database=excipient_db,
                                                                                      chembl_db_file=chembl_db_file)
        return {k: v for k, v in desc_by_term.items() if k not in excipient_by_term}
