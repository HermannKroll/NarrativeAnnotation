import logging

from narrant.preprocessing.enttypes import DRUG, VACCINE
from narrant.vocabularies.drug_vocabulary import DrugVocabulary
from narrant.vocabularies.generic_vocabulary import transform_term2entities_index_to_vocabulary
from narrant.vocabularies.vaccine_vocabulary import VaccineVocabulary


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    drug_term2entities = DrugVocabulary.create_drug_vocabulary_from_chembl(expand_terms=False)
    drug_vocabulary = transform_term2entities_index_to_vocabulary(drug_term2entities, DRUG)
    drug_vocabulary.export_vocabulary_as_tsv("pubpharm_drugs_2022.tsv")

    vaccine_term2entities = VaccineVocabulary.create_vaccine_vocabulary(expand_by_s_and_e=False)
    vaccine_vocabulary = transform_term2entities_index_to_vocabulary(vaccine_term2entities, VACCINE)
    vaccine_vocabulary.export_vocabulary_as_tsv("pubpharm_vaccines_2022.tsv")


if __name__ == '__main__':
    main()
