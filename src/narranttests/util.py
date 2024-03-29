import logging
import os
import tempfile

import narrant.entitylinking.config as cnf
from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.document.document import TaggedEntity
from kgextractiontoolbox.backend.database import Session
from narrant.config import GIT_ROOT_DIR
from narrant.config import PREPROCESS_CONFIG

test_dir = 'src/narranttests/'


def create_test_kwargs():
    config = cnf.Config(PREPROCESS_CONFIG)
    test_kwargs = dict(logger=logging, config=config, collection='TestCollection')
    return test_kwargs


def get_test_resource_filepath(filename):
    return resource_rel_path(filename)


def tmp_rel_path(path):
    return proj_rel_path(test_dir + "tmp/" + path)


def resource_rel_path(path):
    return proj_rel_path(test_dir + "resources/" + path)


def proj_rel_path(path):
    return os.path.join(GIT_ROOT_DIR, path)


def make_test_tempdir():
    return tempfile.mkdtemp()


def is_file_content_equal(file_1, file_2):
    with open(file_1) as f1, open(file_2) as f2:
        return f1.read() == f2.read()


def get_tags_from_database(doc_id=None):
    session = Session.get()
    if doc_id is None:
        result = session.execute("SELECT * FROM tag")
    else:
        result = session.execute(f"SELECT * FROM TAG WHERE document_id={doc_id}")
    for row in result:
        yield TaggedEntity((row["document_id"], row["start"], row["end"],
                            row["ent_str"], row["ent_type"], row["ent_id"]))


def clear_database():
    """DANGER! ONLY USE IN TESTS, NOWHERE IN PRODUCTION CODE!"""
    session = Session.get()
    if Session.is_sqlite:
        session.execute("DELETE FROM tag")
        session.execute("DELETE FROM doc_tagged_by")
