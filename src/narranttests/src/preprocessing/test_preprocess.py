import unittest

import narranttests.util
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.retrieve import iterate_over_all_documents_in_collection
from kgextractiontoolbox.document.extract import read_tagged_documents
from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.document.load_document import document_bulk_load
from narrant.entitylinking import dictpreprocess
from narrant.entitylinking.enttypes import PLANT_FAMILY_GENUS
from narranttests import util
from narranttests.src.preprocessing.tagging.test_pharmdicttagger import assert_tags_pmc_4297_5600


class TestPreprocess(unittest.TestCase):

    def test_dictpreprocess_without_input_file(self):
        util.clear_database()
        workdir = narranttests.util.make_test_tempdir()
        document_bulk_load(util.resource_rel_path('infiles/test_metadictagger/abbrev_tagged.txt'), collection="PREPTEST")
        args = [
            *f"-c PREPTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
        ]
        dictpreprocess.main(args)
        tags = set(util.get_tags_from_database())
        self.assertGreater(len(tags), 0)
        util.clear_database()

    def test_dictpreprocess_ignore_already_tagged_documents(self):
        workdir = narranttests.util.make_test_tempdir()
        with self.assertRaises(SystemExit):
            util.clear_database()
            args = [
                *f"-i {util.resource_rel_path('infiles/json_infiles')} -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
            ]
            dictpreprocess.main(args)
            args = [
                *f"-i {util.resource_rel_path('infiles/json_infiles')} -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
            ]
            dictpreprocess.main(args)
            util.clear_database()

    def test_dictpreprocess_json_input(self):
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {util.resource_rel_path('infiles/json_infiles')} -t DR DF PF E -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
        ]
        dictpreprocess.main(args)
        doc1, doc2 = util.get_tags_from_database(5297), util.get_tags_from_database(5600)
        assert_tags_pmc_4297_5600(self, {repr(t) for t in doc1}, {repr(t) for t in doc2})
        util.clear_database()

    def test_dictpreprocess_sinlge_worker_from_file(self):
        workdir = narranttests.util.make_test_tempdir()
        path = util.resource_rel_path('infiles/test_metadictagger')
        args = [
            *f"-i {path} -t DR DF PF E -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
        ]
        dictpreprocess.main(args)
        doc1, doc2 = util.get_tags_from_database(4297), util.get_tags_from_database(5600)
        assert_tags_pmc_4297_5600(self, {repr(t) for t in doc1}, {repr(t) for t in doc2})
        util.clear_database()

    def test_dictpreprocess_sinlge_worker_from_database(self):
        workdir = narranttests.util.make_test_tempdir()
        document_bulk_load(util.resource_rel_path('infiles/test_metadictagger'), collection="DBINSERTTAGGINGTEST")
        args = [*f"-t DR DF PF E -c DBINSERTTAGGINGTEST --loglevel DEBUG --workdir {workdir} -w 1 -y".split()]
        dictpreprocess.main(args)
        doc1, doc2 = util.get_tags_from_database(4297), util.get_tags_from_database(5600)
        assert_tags_pmc_4297_5600(self, {repr(t) for t in doc1}, {repr(t) for t in doc2})
        util.clear_database()

    def test_dictpreprocess_dual_worker(self):
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {util.resource_rel_path('infiles/test_metadictagger')} -t DR DF PF E -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 2 -y".split()
        ]
        dictpreprocess.main(args)
        doc1, doc2 = util.get_tags_from_database(4297), util.get_tags_from_database(5600)
        assert_tags_pmc_4297_5600(self, {repr(t) for t in doc1}, {repr(t) for t in doc2})
        util.clear_database()

    def test_dictpreprocess_ignore_sections(self):
        in_file = util.get_test_resource_filepath("infiles/test_preprocess/fulltext_19128.json")
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {in_file} -c PREPTEST --loglevel DEBUG --workdir {workdir} -w 2 -y".split()
        ]
        dictpreprocess.main(args)

        doc = list(read_tagged_documents(in_file))[0]
        title_section_len = len(doc.get_text_content(sections=False))
        doc_tags = util.get_tags_from_database(19128)
        for t in doc_tags:
            self.assertGreaterEqual(title_section_len, t.end)
        util.clear_database()

    def test_dictpreprocess_include_sections(self):
        util.clear_database()
        in_file = util.get_test_resource_filepath("infiles/test_preprocess/fulltext_19128.json")
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {in_file} -c PREPTEST --loglevel DEBUG --sections --workdir {workdir} -w 2 -y".split()
        ]
        dictpreprocess.main(args)

        doc = list(read_tagged_documents(in_file))[0]
        title_section_len = len(doc.get_text_content(sections=False))
        doc_len = len(doc.get_text_content(sections=True))
        doc_tags = util.get_tags_from_database(19128)
        tags_in_fulltext = []
        for t in doc_tags:
            if t.end > title_section_len:
                tags_in_fulltext.append(t)
            self.assertGreaterEqual(doc_len, t.end)

        self.assertLess(0, len(tags_in_fulltext))
        util.clear_database()

    def test_dictpreprocess_test_custom_plant_tagger_logic(self):
        util.clear_database()
        in_file = util.get_test_resource_filepath("infiles/test_preprocess/plants.json")
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {in_file} -c PREPTEST --loglevel DEBUG --sections --workdir {workdir} -y".split()
        ]
        dictpreprocess.main(args)

        doc_tags = list([t for t in list(util.get_tags_from_database(10001)) if t.ent_type == PLANT_FAMILY_GENUS])
        print(doc_tags)
        self.assertEqual(0, len(doc_tags))
        doc_tags = list([t for t in list(util.get_tags_from_database(10002)) if t.ent_type == PLANT_FAMILY_GENUS])
        self.assertEqual(1, len(doc_tags))

    def test_dictpreprocess_json_input_issue_out_of_index(self):
        workdir = narranttests.util.make_test_tempdir()
        args = [
            *f"-i {util.resource_rel_path('infiles/test_dictagger/issue_out_of_index.json')} -c PREPTEST_ISSUE_NLTK --loglevel DEBUG --workdir {workdir} -w 1 -y".split()
        ]
        dictpreprocess.main(args)
        session = Session.get()
        docs = list(iterate_over_all_documents_in_collection(session, "PREPTEST_ISSUE_NLTK", consider_tag=True))
        self.assertNotEquals(0, len(docs[0].tags))
        util.clear_database()


if __name__ == '__main__':
    unittest.main()
