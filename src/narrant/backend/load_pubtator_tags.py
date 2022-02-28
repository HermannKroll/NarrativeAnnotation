import argparse
import logging
import sys
from datetime import datetime

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.document.load_document import get_tagger_for_enttype, read_tagger_mapping, UNKNOWN_TAGGER, insert_taggers
from kgextractiontoolbox.backend.models import Document, Tag, DocTaggedBy
from kgextractiontoolbox.progress import print_progress_with_eta
from kgextractiontoolbox.document.document import TaggedDocument, TaggedEntity
from kgextractiontoolbox.document.regex import TAG_LINE_NORMAL

BULK_LOAD_COMMIT_AFTER = 50000
PRINT_ETA_EVERY_K_DOCUMENTS = 100


def tags_bulk_load(tag_file, collection, tagger_mapping=None, logger=logging):
    """
    Bulk load a file in PubTator Format or a directory of PubTator files into the database.
    Iterate over PubTator documents and add Document, Tag and DocTaggedBy objects. Commit after every document.
    :param str tag_file: Path to file or directory
    :param str collection: Identifier of the collection (e.g., PMC)
    :param dict tagger_mapping: Mapping from entity type to tuple (tagger name, tagger version)
    :param logging logger: a logging instance to be used
    :return:
    """
    session = Session.get()

    if tagger_mapping is None:
        logger.warning("No tagger mapping provided. Tags are ignored")

    logger.info('Bulk loading documents into database...')
    sys.stdout.write("Counting tags ...")
    sys.stdout.flush()

    n_docs = 0
    with open(tag_file) as f:
        for line in f:
            n_docs += 1
    sys.stdout.write("\rCounting tags ... found {}\n".format(n_docs))
    sys.stdout.flush()

    logger.info('Retrieving document ids from database...')
    query = session.query(Document.id).filter_by(collection=collection)
    db_doc_ids = set()

    for r in session.execute(query):
        db_doc_ids.add(r[0])
    start_time = datetime.now()

    tag_inserts = []
    doc_tagged_by_inserts = []
    with open(tag_file, 'rt') as f:
        for idx, line in enumerate(f):
            tags = [TaggedEntity(t) for t in TAG_LINE_NORMAL.findall(line)]
            # perform split if composite tags are contained
            if TaggedDocument.pubtator_has_composite_tags(tags):
                tags = TaggedDocument.pubtator_split_composite_tags(tags)

            for tag in tags:
                tagged_ent_types = set()

                if tag.document not in db_doc_ids:
                    logger.warning(f"Tag could not be inserted - document {collection} {tag.document} is missing in db")
                    continue
                # Add tags
                tagged_ent_types.add(tag.ent_type)

                tag_inserts.append(dict(
                    ent_type=tag.ent_type,
                    start=tag.start,
                    end=tag.end,
                    ent_id=tag.ent_id,
                    ent_str=tag.text,
                    document_id=tag.document,
                    document_collection=collection,
                ))

                # Add DocTaggedBy
                for ent_type in tagged_ent_types:
                    tagger_name, tagger_version = get_tagger_for_enttype(tagger_mapping, ent_type)
                    doc_tagged_by_inserts.append(dict(
                        document_id=tag.document,
                        document_collection=collection,
                        tagger_name=tagger_name,
                        tagger_version=tagger_version,
                        ent_type=ent_type,
                    ))

            if idx % BULK_LOAD_COMMIT_AFTER == 0:
                Tag.bulk_insert_values_into_table(session, tag_inserts)
                DocTaggedBy.bulk_insert_values_into_table(session, doc_tagged_by_inserts)

                tag_inserts = []
                doc_tagged_by_inserts = []

            print_progress_with_eta("Adding tags", idx, n_docs, start_time,
                                    print_every_k=PRINT_ETA_EVERY_K_DOCUMENTS)

    logger.info(f'inserting {n_docs}')
    Tag.bulk_insert_values_into_table(session, tag_inserts)
    DocTaggedBy.bulk_insert_values_into_table(session, doc_tagged_by_inserts)

    sys.stdout.write("\rAdding tags ... done in {}\n".format(datetime.now() - start_time))
    logger.info("Added {} tags in {}".format(n_docs, datetime.now() - start_time))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("collection")
    parser.add_argument("-t", "--tagger-map", help="JSON file containing mapping from entity type "
                                                   "to tuple with tagger name and tagger version",
                        required=True)
    parser.add_argument("--logsql", action="store_true", help='logs sql statements')
    args = parser.parse_args()

    tagger_mapping = None
    if args.tagger_map:
        tagger_mapping = read_tagger_mapping(args.tagger_map)
        tagger_list = list(tagger_mapping.values())
        tagger_list.append(UNKNOWN_TAGGER)
        insert_taggers(*tagger_list)

    if args.logsql:
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)

    if not tagger_mapping:
        raise ValueError('No tagger mapping was found - required for tag loading')

    tags_bulk_load(args.input, args.collection, tagger_mapping)


if __name__ == "__main__":
    main()
