from narrant.entity.entity import Entity
from narrant.entitylinking.enttypes import DISEASE, GENE, CHEMICAL, EXCIPIENT, DRUG, CHEMBL_CHEMICAL, \
    SPECIES, \
    PLANT_FAMILY_GENUS, LAB_METHOD, METHOD, HEALTH_STATUS, TARGET

DOSAGE_FORM_PREDICATE = "administered"
METHOD_PREDICATE = "method"
ASSOCIATED_PREDICATE = "associated"
ASSOCIATED_PREDICATE_UNSURE = ASSOCIATED_PREDICATE

ENTITY_TYPE_EXPANSION = dict(
    Chemical=[CHEMICAL, EXCIPIENT, DRUG],
    Method=[METHOD, LAB_METHOD],
    Target=[TARGET, GENE]
)
PREDICATE_EXPANSION = dict(
    interacts=['interacts', 'metabolises', 'inhibits'],
    decreases=['decreases', 'inhibits']
)
SYMMETRIC_PREDICATES = {"interacts", "associated", "induces", "decreases", "administered", "method"}
PREDICATE_TYPING = {'treats': ({CHEMICAL, DRUG, CHEMBL_CHEMICAL, EXCIPIENT, PLANT_FAMILY_GENUS},
                               {DISEASE, SPECIES, HEALTH_STATUS}),
                    #               'administered': ({DOSAGE_FORM},
                    #                                {SPECIES, DISEASE, CHEMICAL, DRUG, CHEMBL_CHEMICAL, EXCIPIENT,
                    #                                 PLANT_FAMILY_GENUS, DOSAGE_FORM, LAB_METHOD, METHOD}),
                    #              'method': ({METHOD, LAB_METHOD},
                    #                        {SPECIES, DISEASE, CHEMICAL, DRUG, CHEMBL_CHEMICAL, EXCIPIENT,
                    #                        PLANT_FAMILY_GENUS, DOSAGE_FORM, LAB_METHOD, METHOD}),
                    'induces': ({CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, DISEASE, PLANT_FAMILY_GENUS},
                                {CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, DISEASE, PLANT_FAMILY_GENUS}),
                    'decreases': ({CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, DISEASE, PLANT_FAMILY_GENUS},
                                  {CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, DISEASE, PLANT_FAMILY_GENUS}),
                    'interacts': (
                    {CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, GENE, PLANT_FAMILY_GENUS, TARGET, 'ArabidopsisGene'},
                    {CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, GENE, PLANT_FAMILY_GENUS, TARGET, 'ArabidopsisGene'}),
                    'metabolises': ({GENE, TARGET, 'ArabidopsisGene'},
                                    {CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, PLANT_FAMILY_GENUS}),
                    'inhibits': ({CHEMICAL, DRUG, EXCIPIENT, CHEMBL_CHEMICAL, PLANT_FAMILY_GENUS},
                                 {GENE, TARGET, 'ArabidopsisGene'}),
                    }


def sort_symmetric_arguments(subject_id, subject_type, object_id, object_type):
    if subject_id < object_id:
        return subject_id, subject_type, object_id, object_type
    else:
        return object_id, object_type, subject_id, subject_type


def are_subject_and_object_correctly_ordered(subject_id, object_id):
    if subject_id < object_id:
        return True
    else:
        return False


def have_entities_correct_order(arg1: Entity, arg2: Entity):
    return arg1.entity_id < arg2.entity_id
