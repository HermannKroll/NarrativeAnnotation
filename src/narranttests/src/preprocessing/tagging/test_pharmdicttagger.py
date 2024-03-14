import os
import unittest

import narrant.entitylinking.enttypes as et
import narranttests.util as util
from kgextractiontoolbox.document.document import parse_tag_list, TaggedEntity, TaggedDocument
from kgextractiontoolbox.document.extract import read_tagged_documents
from narrant.entitylinking.pharmacy.pharmdicttagger import PharmDictTagger


class TestMetadictagger(unittest.TestCase):
    ent_type_set = {et.DRUG, et.EXCIPIENT, et.DOSAGE_FORM, et.PLANT_FAMILY_GENUS}

    def test_init(self):
        metatag = TestMetadictagger.make_metatag(self.ent_type_set)
        self.assertSetEqual(set(metatag._vocabs.keys()), TestMetadictagger.ent_type_set)
        self.assertIn("MESH:D007267", metatag._vocabs[et.DOSAGE_FORM]["injection"])
        self.assertIn("Agave", metatag._vocabs[et.PLANT_FAMILY_GENUS]["agave"])
        self.assertIn("CHEMBL412873", metatag._vocabs[et.DRUG]["sparteine"])

    def test_tag(self):
        in_1 = util.get_test_resource_filepath("infiles/test_metadictagger/4297.txt")
        out_1 = util.tmp_rel_path("out/4297.txt")
        os.makedirs(os.path.dirname(out_1), exist_ok=True)
        in_2 = util.get_test_resource_filepath("infiles/test_metadictagger/5600.txt")
        out_2 = util.tmp_rel_path("out/5600.txt")
        metatag = TestMetadictagger.make_metatag(self.ent_type_set)
        metatag._tag(in_1, out_1)
        metatag._tag(in_2, out_2)
        tags_1 = [repr(tag) for tag in parse_tag_list(out_1)]
        tags_2 = [repr(tag) for tag in parse_tag_list(out_2)]

        assert_tags_pmc_4297_5600(self, tags_1, tags_2)

    def test_custom_abbreviation(self):
        in_file = util.get_test_resource_filepath("infiles/test_metadictagger/abbreviations.txt")
        metatag = TestMetadictagger.make_metatag(self.ent_type_set)
        out_file = metatag.tag_doc([d for d in read_tagged_documents(in_file)][0])
        out_file.clean_tags()
        self.assertIn(TaggedEntity(None, 32926486, 716, 718, "eo", "Excipient", "CHEMBL1743219"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926486, 1234, 1236, "eo", "Excipient", "CHEMBL1743219"), out_file.tags)

    def test_custom_abbreviation_with_closing_space(self):
        in_file = util.get_test_resource_filepath("infiles/test_metadictagger/h2o2space_test.txt")
        metatag = TestMetadictagger.make_metatag(self.ent_type_set)
        out_file = metatag.tag_doc([d for d in read_tagged_documents(in_file)][0])
        out_file.clean_tags()
        self.assertIn(TaggedEntity(None, 32926513, 61, 78, "hydrogen peroxide", "Excipient", "CHEMBL71595"),
                      out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 91, 108, "hydrogen peroxide", "Excipient", "CHEMBL71595"),
                      out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 110, 117, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 345, 352, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 462, 469, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 488, 495, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 573, 580, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 666, 673, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 949, 956, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)
        self.assertIn(TaggedEntity(None, 32926513, 1172, 1179, "h 2 o 2", "Excipient", "CHEMBL71595"), out_file.tags)

    def test_different_min_full_tag_lengths(self):
        ent_type_set = {et.DRUG, et.HEALTH_STATUS}
        tagger = TestMetadictagger.make_metatag(ent_type_set)

        doc_text = "Man should not be tagged, men should. The drug tagger should tag metformin but not drug."
        doc = TaggedDocument(title=doc_text, abstract="", id=1)
        doc = tagger.tag_doc(doc)
        doc.sort_tags()
        self.assertEqual(2, len(doc.tags))

        # <Entity 26,29,men,HealthStatus,MESH:D008571>
        actual_tag = doc.tags[0]
        expected_tag = TaggedEntity(None, 1, 26, 29, "men", et.HEALTH_STATUS, "MESH:D008571")
        self.assertEqual(expected_tag, actual_tag)

        # <Entity 65,74,metformin,Drug,CHEMBL1431>
        actual_tag = doc.tags[1]
        expected_tag = TaggedEntity(None, 1, 65, 74, "metformin", et.DRUG, "CHEMBL1431")
        self.assertEqual(expected_tag, actual_tag)

    @staticmethod
    def make_metatag(ent_type_set) -> PharmDictTagger:
        tagger = PharmDictTagger(ent_type_set, util.create_test_kwargs())
        tagger.prepare()
        return tagger


def assert_tags_pmc_4297_5600(test_suit, tags_4297, tags_5600):
    test_suit.assertIn("<Entity 400,426,intraventricular injection,DosageForm,MESH:D007276>", tags_4297)
    test_suit.assertIn("<Entity 637,646,injection,DosageForm,MESH:D007267>", tags_4297)

    test_suit.assertIn("<Entity 210,219,sparteine,Drug,CHEMBL412873>", tags_5600)
    test_suit.assertIn("<Entity 1311,1326,2-aminopyridine,Drug,CHEMBL21619>", tags_5600)
    test_suit.assertIn("<Entity 827,836,potassium,Excipient,CHEMBL1201290>", tags_5600)


if __name__ == '__main__':
    unittest.main()
