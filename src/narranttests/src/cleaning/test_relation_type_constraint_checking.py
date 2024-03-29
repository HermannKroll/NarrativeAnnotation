import unittest

from kgextractiontoolbox.cleaning.relation_type_constraints import RelationTypeConstraintStore
from narrant.entitylinking.enttypes import DISEASE, GENE, CHEMICAL, DOSAGE_FORM, EXCIPIENT, DRUG, \
    SPECIES, \
    PLANT_FAMILY_GENUS, LAB_METHOD, METHOD
from narranttests import util

PREDICATE_TYPING_TEST = {'treats': ({CHEMICAL, DRUG, EXCIPIENT, PLANT_FAMILY_GENUS},
                                    {DISEASE, SPECIES}),
                         'administered': ({DOSAGE_FORM}, {"All"}),
                         'method': ({METHOD, LAB_METHOD}, {"All"}),
                         'induces': ({CHEMICAL, DRUG, EXCIPIENT, DISEASE, PLANT_FAMILY_GENUS},
                                     {CHEMICAL, DRUG, EXCIPIENT, DISEASE, PLANT_FAMILY_GENUS}),
                         'decreases': ({CHEMICAL, DRUG, EXCIPIENT, DISEASE, PLANT_FAMILY_GENUS},
                                       {CHEMICAL, DRUG, EXCIPIENT, DISEASE, PLANT_FAMILY_GENUS}),
                         'interacts': ({CHEMICAL, DRUG, EXCIPIENT, GENE, PLANT_FAMILY_GENUS},
                                       {CHEMICAL, DRUG, EXCIPIENT, GENE, PLANT_FAMILY_GENUS}),
                         'metabolises': ({GENE},
                                         {CHEMICAL, DRUG, EXCIPIENT, PLANT_FAMILY_GENUS}),
                         'inhibits': ({CHEMICAL, DRUG, EXCIPIENT, PLANT_FAMILY_GENUS},
                                      {GENE}),
                         }


class RelationTypeConstraintChecking(unittest.TestCase):

    def test_pharm_constraint_store(self):
        store = RelationTypeConstraintStore()
        store.load_from_json(util.get_test_resource_filepath('cleaning/pharm_relation_type_constraints.json'))

        for relation in PREDICATE_TYPING_TEST:
            self.assertIn(relation, store.constraints)
            subjects = PREDICATE_TYPING_TEST[relation][0]
            objects = PREDICATE_TYPING_TEST[relation][1]
            subjects_store = set(store.constraints[relation]["subjects"])
            objects_store = set(store.constraints[relation]["objects"])

            self.assertEqual(subjects, subjects.intersection(subjects_store), msg=f'comparison failed for: {relation}')
            self.assertEqual(subjects_store, subjects.intersection(subjects_store),
                             msg=f'comparison failed for: {relation}')
            self.assertEqual(objects, objects.intersection(objects_store), msg=f'comparison failed for: {relation}')
            self.assertEqual(objects_store, objects.intersection(objects_store),
                             msg=f'comparison failed for: {relation}')
