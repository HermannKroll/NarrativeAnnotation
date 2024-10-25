import unittest
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag, Document
from narrant.cleaning.clean_tag_gene_ids import clean_gene_ids_in_tag
from narrant.entitylinking.enttypes import GENE


class TestCleanTagGeneIds(unittest.TestCase):

    def test_clean_tags(self):
        session = Session.get()
        document_values = [dict(id=1, collection="TEST_TAG", title="title", abstract="abstract"),
                           dict(id=2, collection="TEST_TAG", title="title", abstract="abstract"),
                           dict(id=3, collection="TEST_TAG", title="title", abstract="abstract")]
        tag_values = [dict(id=100000, ent_type=GENE, ent_id="A; B", ent_str="AS", start=0, end=0, document_id=1,
                           document_collection="TEST_TAG"),
                      dict(id=100001, ent_type="AT", ent_id="T", ent_str="ABS", start=0, end=0, document_id=2,
                           document_collection="TEST_TAG"),
                      dict(id=100002, ent_type=GENE, ent_id="C;D;E", ent_str="GH", start=0, end=0, document_id=3,
                           document_collection="TEST_TAG"),
                      dict(id=100003, ent_type="AT", ent_id="T;y", ent_str="ABS", start=0, end=0, document_id=2,
                           document_collection="TEST_TAG")
                      ]
        Document.bulk_insert_values_into_table(session, document_values)
        Tag.bulk_insert_values_into_table(session, tag_values)
        clean_gene_ids_in_tag()
        allowed_tags = [(GENE, "A"), (GENE, "B"), (GENE, "C"), (GENE, "D"), (GENE, "E"), ("AT", "T"), ("AT", "T;y")]

        for row in session.query(Tag):
            key = (row.ent_type, row.ent_id)
            self.assertIn(key, allowed_tags)
