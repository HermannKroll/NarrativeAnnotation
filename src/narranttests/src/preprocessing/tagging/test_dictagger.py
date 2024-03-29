import unittest

import kgextractiontoolbox.document.document as doc
from kgextractiontoolbox.document.extract import read_tagged_documents
from kgextractiontoolbox.entitylinking.tagging.dictagger import split_indexed_words, DictTagger
from kgextractiontoolbox.entitylinking.tagging.vocabulary import expand_vocabulary_term
from narrant.entitylinking.enttypes import DRUG
from narrant.entitylinking.pharmacy.dosage import DosageFormTagger
from narrant.entitylinking.pharmacy.drug import DrugTagger
from narranttests.util import create_test_kwargs, get_test_resource_filepath, resource_rel_path


class TestDictagger(unittest.TestCase):


    def test_tag(self):
        tagger = DosageFormTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "protein": {"Desc1"},
            "proteins": {"Desc1"},
            "phorbol": {"Desc2", "Desc3"},
            "protein secretion": {"Desc4"},
            "protein synthesis": {"Desc5"}
        }

        doc_to_tags = list(read_tagged_documents(get_test_resource_filepath("infiles/test_dictagger")))
        tag_strings = []
        for d in doc_to_tags:
            tagger.tag_doc(d)
            for tag in d.tags:
                tag_strings.append(repr(tag))

        self.assertIn("<Entity 0,8,proteins,DosageForm,Desc1>", tag_strings)
        self.assertIn("<Entity 1104,1112,proteins,DosageForm,Desc1>", tag_strings)
        self.assertIn("<Entity 1104,1112,proteins,DosageForm,Desc1>", tag_strings)
        self.assertIn("<Entity 1609,1626,protein secretion,DosageForm,Desc4>", tag_strings)

    def test_abbreviation_check(self):
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "aspirin": {"Desc1"},
            "asa": {"Desc1"},
        }

        doc_to_tags = list(read_tagged_documents(get_test_resource_filepath("infiles/test_dictagger")))
        tag_strings = []
        for d in doc_to_tags:
            tagger.tag_doc(d)
            for tag in d.tags:
                tag_strings.append(repr(tag))

        self.assertIn("<Entity 21,28,aspirin,Drug,Desc1>", tag_strings)
        self.assertIn("<Entity 30,33,asa,Drug,Desc1>", tag_strings)
        self.assertIn("<Entity 52,55,asa,Drug,Desc1>", tag_strings)

    def test_abbreviation_not_allowed_check(self):
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "aspirin": {"Desc1"},
            "asa": {"Desc1"},
            "metformin": {"Desc2"}
        }

        doc_to_tags = list(
            read_tagged_documents(resource_rel_path("infiles/test_dictagger/abbreviation_test_not_allowed.txt")))
        tag_strings = []
        for d in doc_to_tags:
            tagger.tag_doc(d)
            for tag in d.tags:
                tag_strings.append(repr(tag))

        self.assertIn("<Entity 52,61,metformin,Drug,Desc2>", tag_strings)
        self.assertNotIn("ASA", tag_strings)


    def test_text_tagging_simvastatin(self):
        text = "Simvastatin (ST) is a drug. Simvastatin is cool. Cool is also simVAStatin. ST is simvastatine."
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "simvastatin": {"d1"},
            "simvastatine": {"d1"}
        }

        doc1 = doc.TaggedDocument(title=text, abstract="", id=1)
        tagger.tag_doc(doc1)
        doc1.sort_tags()

        self.assertEqual(6, len(doc1.tags))
        positions = [(0, 11), (13, 15), (28, 39), (62, 73), (75, 77), (81, 93)]

        for idx, tag in enumerate(doc1.tags):
            self.assertEqual(DRUG, tag.ent_type)
            self.assertEqual("d1", tag.ent_id)
            self.assertEqual(positions[idx][0], tag.start)
            self.assertEqual(positions[idx][1], tag.end)

    def test_text_tagging_simvastatin_title_abstract(self):
        title = "Simvastatin (ST) is a drug."
        abstract = "Simvastatin is cool. Cool is also simVAStatin. ST is simvastatine."
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "simvastatin": {"d1"},
            "simvastatine": {"d1"}
        }

        doc1 = doc.TaggedDocument(title=title, abstract=abstract, id=1)
        tagger.tag_doc(doc1)
        doc1.sort_tags()

        self.assertEqual(6, len(doc1.tags))
        positions = [(0, 11), (13, 15), (28, 39), (62, 73), (75, 77), (81, 93)]

        for idx, tag in enumerate(doc1.tags):
            self.assertEqual(DRUG, tag.ent_type)
            self.assertEqual("d1", tag.ent_id)
            self.assertEqual(positions[idx][0], tag.start)
            self.assertEqual(positions[idx][1], tag.end)

    def test_text_tagging_long_entities(self):
        title = "complex disease"
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "complex disease": {"d1"},
            "disease": {"d2"}
        }

        doc1 = doc.TaggedDocument(title=title, abstract="", id=1)
        tagger.tag_doc(doc1)
        self.assertEqual(2, len(doc1.tags))

        # now the smaller tag should be removed
        doc1.clean_tags()
        doc1.sort_tags()

        self.assertEqual(1, len(doc1.tags))
        tag = doc1.tags[0]
        self.assertEqual(0, tag.start)
        self.assertEqual(15, tag.end)
        self.assertEqual("d1", tag.ent_id)
        self.assertEqual(DRUG, tag.ent_type)

    def test_text_tagging_simvastatin_in_sections(self):
        text = "Simvastatin (ST) is a drug. Simvastatin is cool. Cool is also simVAStatin. ST is simvastatine."
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "simvastatin": {"d1"},
            "simvastatine": {"d1"}
        }

        doc1 = doc.TaggedDocument(title="a", abstract="", id=1)
        doc1.sections.append(doc.DocumentSection(position=0, title="", text=text))

        # test no tags when sections are not considered
        tagger.tag_doc(doc1)
        doc1.sort_tags()
        self.assertEqual(0, len(doc1.tags))

        # test consider sections
        tagger.tag_doc(doc1, consider_sections=True)
        doc1.sort_tags()
        self.assertEqual(6, len(doc1.tags))
        positions = [(0, 11), (13, 15), (28, 39), (62, 73), (75, 77), (81, 93)]

        for idx, tag in enumerate(doc1.tags):
            self.assertEqual(DRUG, tag.ent_type)
            self.assertEqual("d1", tag.ent_id)
            # space between each section
            self.assertEqual(positions[idx][0] + 3, tag.start)
            self.assertEqual(positions[idx][1] + 3, tag.end)

    def test_text_tagging_simvastatin_in_section_spaces(self):
        text = "Simvastatin (ST) is a drug. Simvastatin is cool. Cool is also simVAStatin. ST is simvastatine."
        tagger = DrugTagger(**create_test_kwargs())
        tagger.desc_by_term = {
            "simvastatin": {"d1"},
            "simvastatine": {"d1"}
        }

        doc1 = doc.TaggedDocument(title="a", abstract="", id=1)
        doc1.sections.append(doc.DocumentSection(position=0, title="", text=""))
        doc1.sections.append(doc.DocumentSection(position=0, title="", text=""))
        doc1.sections.append(doc.DocumentSection(position=0, title="", text=text))

        # test no tags when sections are not considered
        tagger.tag_doc(doc1)
        doc1.sort_tags()
        self.assertEqual(0, len(doc1.tags))

        # test consider sections
        tagger.tag_doc(doc1, consider_sections=True)
        doc1.sort_tags()
        self.assertEqual(6, len(doc1.tags))
        positions = [(0, 11), (13, 15), (28, 39), (62, 73), (75, 77), (81, 93)]

        for idx, tag in enumerate(doc1.tags):
            self.assertEqual(DRUG, tag.ent_type)
            self.assertEqual("d1", tag.ent_id)
            # space between each section
            self.assertEqual(positions[idx][0] + 7, tag.start)
            self.assertEqual(positions[idx][1] + 7, tag.end)


if __name__ == '__main__':
    unittest.main()
