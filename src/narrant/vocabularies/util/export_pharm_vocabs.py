import logging

from narrant.preprocessing.enttypes import DRUG, VACCINE, CHEMICAL, DOSAGE_FORM, DISEASE, EXCIPIENT, PLANT_FAMILY_GENUS, \
    METHOD, LAB_METHOD
from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.vocabularies.chemical_vocabulary import ChemicalVocabulary
from narrant.vocabularies.disease_vocabulary import DiseaseVocabulary
from narrant.vocabularies.dosageform_vocabulary import DosageFormVocabulary
from narrant.vocabularies.drug_vocabulary import DrugVocabulary
from narrant.vocabularies.excipient_vocabulary import ExcipientVocabulary
from narrant.vocabularies.generic_vocabulary import transform_term2entities_index_to_vocabulary
from narrant.vocabularies.labmethod_vocabulary import LabMethodVocabulary
from narrant.vocabularies.method_vocabulary import MethodVocabulary
from narrant.vocabularies.plant_family_genus import PlantFamilyGenusVocabulary
from narrant.vocabularies.vaccine_vocabulary import VaccineVocabulary


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    chemical_term2entities = ChemicalVocabulary.create_chembl_chemical_vocabulary()
    chemical_vocabulary = transform_term2entities_index_to_vocabulary(chemical_term2entities, CHEMICAL)
    chemical_vocabulary.export_vocabulary_as_tsv("pubpharm_chemical_2022.tsv")

    drug_term2entities = DrugVocabulary.create_drug_vocabulary_from_chembl(expand_terms=False)
    drug_vocabulary = transform_term2entities_index_to_vocabulary(drug_term2entities, DRUG)
    drug_vocabulary.export_vocabulary_as_tsv("pubpharm_drugs_2022.tsv")

    dosage_term2entities = DosageFormVocabulary.create_dosage_form_vocabulary(expand_by_s_and_e=False)
    dosage_vocabulary = transform_term2entities_index_to_vocabulary(dosage_term2entities, DOSAGE_FORM)
    dosage_vocabulary.export_vocabulary_as_tsv("pubpharm_dosage_forms_2022.tsv")

    disease_term2entities = DiseaseVocabulary.create_disease_vocabulary(expand_by_s_and_e=False)
    disease_vocabulary = transform_term2entities_index_to_vocabulary(disease_term2entities, DISEASE)
    disease_vocabulary.export_vocabulary_as_tsv("pubpharm_diseases_2022.tsv")

    excipient_term2entities = ExcipientVocabulary.create_excipient_vocabulary()
    excipient_vocabulary = transform_term2entities_index_to_vocabulary(excipient_term2entities, EXCIPIENT)
    excipient_vocabulary.export_vocabulary_as_tsv("pubpharm_excipients_2022.tsv")

    methods_term2entities = MethodVocabulary.create_method_vocabulary(expand_terms=False)
    methods_vocabulary = transform_term2entities_index_to_vocabulary(methods_term2entities, METHOD)
    methods_vocabulary.export_vocabulary_as_tsv("pubpharm_methods_2022.tsv")

    labmethods_term2entities = LabMethodVocabulary.create_lab_method_vocabulary(expand_terms=False)
    labmethods_vocabulary = transform_term2entities_index_to_vocabulary(labmethods_term2entities, LAB_METHOD)
    labmethods_vocabulary.export_vocabulary_as_tsv("pubpharm_labmethods_2022.tsv")

    plants_term2entities = PlantFamilyGenusVocabulary.read_plant_family_genus_vocabulary(expand_terms=False)
    plants_vocabulary = transform_term2entities_index_to_vocabulary(plants_term2entities, PLANT_FAMILY_GENUS)
    plants_vocabulary.export_vocabulary_as_tsv("pubpharm_plants_2022.tsv")

    vaccine_term2entities = VaccineVocabulary.create_vaccine_vocabulary(expand_by_s_and_e=False)
    vaccine_vocabulary = transform_term2entities_index_to_vocabulary(vaccine_term2entities, VACCINE)
    vaccine_vocabulary.export_vocabulary_as_tsv("pubpharm_vaccines_2022.tsv")

    pubpharm_vocab_all = Vocabulary("")
    pubpharm_vocab_all.add_vocabulary(chemical_vocabulary)
    pubpharm_vocab_all.add_vocabulary(drug_vocabulary)
    pubpharm_vocab_all.add_vocabulary(dosage_vocabulary)
    pubpharm_vocab_all.add_vocabulary(disease_vocabulary)
    pubpharm_vocab_all.add_vocabulary(excipient_vocabulary)
    pubpharm_vocab_all.add_vocabulary(methods_vocabulary)
    pubpharm_vocab_all.add_vocabulary(labmethods_vocabulary)
    pubpharm_vocab_all.add_vocabulary(plants_vocabulary)
    pubpharm_vocab_all.add_vocabulary(vaccine_vocabulary)
    pubpharm_vocab_all.export_vocabulary_as_tsv("pubpharm_2022.tsv")


if __name__ == '__main__':
    main()
