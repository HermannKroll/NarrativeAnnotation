import hashlib
import logging
import unicodedata
from datetime import datetime
from io import StringIO
from typing import List, Set

from sqlalchemy import Column, String, Integer, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, \
    BigInteger, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from narrant.preprocessing.enttypes import GENE, SPECIES
from narrant.progress import print_progress_with_eta
from narrant.pubtator.regex import ILLEGAL_CHAR

Base = declarative_base()
BULK_INSERT_AFTER_K = 100000
POSTGRES_COPY_LOAD_AFTER_K = 1000000


def chunks_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def postgres_sanitize_str(string: str) -> str:
    """
    Sanitizes a string for a postgres COPY insert
    :param string: a string
    :return: the sanitized string
    """
    return string.replace('\\', '\\\\')


def postgres_copy_insert(session, values: List[dict], table_name: str):
    """
    Performs a fast COPY INSERT operation for Postgres Databases
    Do not check any constraints!
    :param session: the current session object
    :param values: a list of dictionary objects (they must correspond to the table)
    :param table_name: the table name to insert into
    :return: None
    """
    for values_chunk in chunks_list(values, POSTGRES_COPY_LOAD_AFTER_K):
        connection = session.connection().connection
        memory_file = StringIO()
        attribute_keys = list(values_chunk[0].keys())
        for idx, v in enumerate(values_chunk):
            mem_str = '{}'.format('\t'.join([postgres_sanitize_str(str(v[k])) for k in attribute_keys]))
            if idx == 0:
                memory_file.write(mem_str)
            else:
                memory_file.write(f'\n{mem_str}')
        cursor = connection.cursor()
        logging.debug(f'Executing copy from {table_name}...')
        memory_file.seek(0)
        cursor.copy_from(memory_file, table_name, sep='\t', columns=attribute_keys)
        logging.debug('Committing...')
        connection.commit()
        memory_file.close()


def bulk_insert_values_to_table(session, values: List[dict], table_class, print_progress=False):
    """
    Performs a bulk insert to a database table
    :param session: the current session object
    :param values: a list of dictionary objects that correspond to the table
    :param table_class: the table class to insert into
    :return: None
    """
    task_size = 1 + int(len(values) / BULK_INSERT_AFTER_K)
    start_time = datetime.now()
    for idx, chunk_values in enumerate(chunks_list(values, BULK_INSERT_AFTER_K)):
        if print_progress:
            print_progress_with_eta("Inserting values...", idx, task_size, start_time, print_every_k=1)
        session.bulk_insert_mappings(table_class, chunk_values)
        session.commit()


class DatabaseTable:
    """
    Every Database Class that inherits from this class will have this bulk insert method available as a class method
    """

    @classmethod
    def bulk_insert_values_into_table(cls, session, values: List[dict], check_constraints=True, print_progress=False):
        if not values or len(values) == 0:
            return
        logging.debug(f'Inserting values into {cls.__tablename__}...')
        if session.is_postgres and not check_constraints:
            postgres_copy_insert(session, values, cls.__tablename__)
        else:
            bulk_insert_values_to_table(session, values, cls, print_progress)
        logging.debug(f'{len(values)} values have been inserted')


class Document(Base, DatabaseTable):
    __tablename__ = "document"
    __table_args__ = (
        PrimaryKeyConstraint('collection', 'id', sqlite_on_conflict='IGNORE'),
    )
    collection = Column(String)
    id = Column(BigInteger)
    title = Column(String, nullable=False)
    abstract = Column(String, nullable=False)
    fulltext = Column(String)

    date_inserted = Column(DateTime, nullable=False, default=datetime.now)

    def __str__(self):
        return "{}{}".format(self.collection, self.id)

    def __repr__(self):
        return "<Document {}{}>".format(self.collection, self.id)

    def to_pubtator(self):
        return Document.create_pubtator(self.id, self.title, self.abstract)

    @staticmethod
    def create_pubtator(did, title: str, abstract: str):
        if title:
            title = unicodedata.normalize('NFD', title)
            title = ILLEGAL_CHAR.sub("", title).strip()
        else:
            title = ""
        if abstract:
            abstract = unicodedata.normalize('NFD', abstract)
            abstract = ILLEGAL_CHAR.sub("", abstract).strip()
        else:
            abstract = ""
        return "{id}|t|{tit}\n{id}|a|{abs}\n".format(id=did, tit=title, abs=abstract)

    @staticmethod
    def sanitize(to_sanitize):
        to_sanitize = unicodedata.normalize('NFD', to_sanitize)
        to_sanitize = ILLEGAL_CHAR.sub("", to_sanitize).strip()
        return to_sanitize

    @staticmethod
    def get_document_ids_for_collection(session, collection: str) -> Set[int]:
        query = session.query(Document.id).filter(Document.collection == collection)
        ids = set()
        for r in query:
            ids.add(int(r[0]))
        return ids


class Tagger(Base, DatabaseTable):
    __tablename__ = "tagger"
    __table_args__ = (
        PrimaryKeyConstraint('name', 'version', sqlite_on_conflict='IGNORE'),
    )
    name = Column(String, primary_key=True)
    version = Column(String, primary_key=True)


class DocTaggedBy(Base, DatabaseTable):
    __tablename__ = "doc_tagged_by"
    __table_args__ = (
        ForeignKeyConstraint(('document_id', 'document_collection'), ('document.id', 'document.collection')
                             , sqlite_on_conflict='IGNORE'),
        ForeignKeyConstraint(('tagger_name', 'tagger_version'), ('tagger.name', 'tagger.version')
                             , sqlite_on_conflict='IGNORE'),
        PrimaryKeyConstraint('document_id', 'document_collection', 'tagger_name', 'tagger_version', 'ent_type'
                             , sqlite_on_conflict='IGNORE'),
    )
    document_id = Column(BigInteger, nullable=False, index=True)
    document_collection = Column(String, nullable=False, index=True)
    tagger_name = Column(String, nullable=False)
    tagger_version = Column(String, nullable=False)
    ent_type = Column(String, nullable=False)
    date_inserted = Column(DateTime, nullable=False, default=datetime.now)


class Tag(Base, DatabaseTable):
    __tablename__ = "tag"
    __table_args__ = (
        ForeignKeyConstraint(('document_id', 'document_collection'), ('document.id', 'document.collection'),
                             sqlite_on_conflict='IGNORE'),
        UniqueConstraint('document_id', 'document_collection', 'start', 'end', 'ent_type', 'ent_id',
                         sqlite_on_conflict='IGNORE'),
        PrimaryKeyConstraint('id', sqlite_on_conflict='IGNORE')
    )

    id = Column(Integer)
    ent_type = Column(String, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    ent_id = Column(String, nullable=False)
    ent_str = Column(String, nullable=False)
    document_id = Column(BigInteger, nullable=False, index=True)
    document_collection = Column(String, nullable=False, index=True)

    def __eq__(self, other):
        return self.ent_type == other.ent_type and self.start == other.start and self.end == other.end and \
               self.ent_id == other.ent_id and self.ent_str == other.ent_str and \
               self.document_id == other.document_id and self.document_collection == other.document_collection

    def __hash__(self):
        return hash((self.ent_type, self.start, self.end, self.ent_id, self.ent_str, self.document_id,
                     self.document_collection))

    @staticmethod
    def create_pubtator(did, start, end, ent_str, ent_type, ent_id):
        return "{}\t{}\t{}\t{}\t{}\t{}\n".format(did, start, end, ent_str, ent_type, ent_id)

    def to_pubtator(self):
        return Tag.create_pubtator(self.document_id, self.start, self.end, self.ent_str, self.ent_type, self.ent_id)

    @staticmethod
    def get_gene_ids(session):
        logging.info('Querying gene ids in Tag table...')
        gene_ids_in_db = set()
        q = session.query(Tag.ent_id.distinct()).filter(Tag.ent_type == GENE)
        for r in session.execute(q):
            try:
                gene_ids_in_db.add(int(r[0]))
            except ValueError:
                continue
        logging.info('{} gene ids retrieved'.format(len(gene_ids_in_db)))
        return gene_ids_in_db

    @staticmethod
    def get_species_ids(session):
        logging.info('Querying species ids in Tag table...')
        gene_ids_in_db = set()
        q = session.query(Tag.ent_id.distinct()).filter(Tag.ent_type == SPECIES)
        for r in session.execute(q):
            try:
                gene_ids_in_db.add(int(r[0]))
            except ValueError:
                continue
        logging.info('{} species ids retrieved'.format(len(gene_ids_in_db)))
        return gene_ids_in_db


class DocumentTranslation(Base, DatabaseTable):
    __tablename__ = "document_translation"
    __table_args__ = (
        PrimaryKeyConstraint('document_id', 'document_collection', sqlite_on_conflict='IGNORE'),
    )
    document_id = Column(BigInteger)
    document_collection = Column(String)
    source_doc_id = Column(String, nullable=False)
    md5 = Column(String, nullable=False)
    date_inserted = Column(DateTime, nullable=False, default=datetime.now)
    source = Column(String)

    @staticmethod
    def text_to_md5_hash(text: str) -> str:
        m = hashlib.md5()
        m.update(text.encode())
        return m.hexdigest()


class DocumentClassification(Base, DatabaseTable):
    __tablename__ = "document_classification"
    __table_args__ = (
        PrimaryKeyConstraint('document_id', 'document_collection', 'classification', sqlite_on_conflict='IGNORE'),
        ForeignKeyConstraint(('document_id', 'document_collection'), ('document.id', 'document.collection'))
    )
    document_id = Column(BigInteger)
    document_collection = Column(String)
    classification = Column(String)
    explanation = Column(String)

    @staticmethod
    def get_document_ids_for_class(session, document_collection: str, document_class: str) -> Set[int]:
        query = session.query(DocumentClassification.document_id).filter(
            DocumentClassification.classification == document_class).filter(
            DocumentClassification.document_collection == document_collection
        )
        ids = set()
        for r in query:
            ids.add(int(r[0]))
        return ids
