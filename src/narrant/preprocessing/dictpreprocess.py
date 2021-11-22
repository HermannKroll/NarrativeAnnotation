import logging
import multiprocessing
import os
import shutil
import tempfile
from argparse import ArgumentParser
from datetime import datetime
from typing import Iterable, Set, List

from narrant.backend.database import Session
from narrant.backend.load_document import document_bulk_load
from narrant.backend.models import DocTaggedBy, Document
from narrant.config import PREPROCESS_CONFIG
from narrant.preprocessing.config import Config
from narrant.preprocessing.enttypes import TAG_TYPE_MAPPING, DALL
from narrant.preprocessing.preprocess import init_preprocess_logger, init_sqlalchemy_logger, \
    get_untagged_doc_ids_by_ent_type
from narrant.preprocessing.tagging.metadictagger import MetaDicTagger, PharmDictTaggerFactory
from narrant.progress import Progress
from narrant.pubtator import count
from narrant.pubtator.document import TaggedDocument, TaggedEntity
from narrant.pubtator.extract import read_pubtator_documents
from narrant.pubtator.sanitize import filter_and_sanitize
from narrant.util.multiprocessing.ConsumerWorker import ConsumerWorker
from narrant.util.multiprocessing.ProducerWorker import ProducerWorker
from narrant.util.multiprocessing.Worker import Worker

BULK_INSERT_AFTER_K = 1000


def prepare_input(in_file: str, out_file: str, logger: logging.Logger, ent_types: Iterable[str],
                  collection: str) -> Set[int]:
    if not os.path.exists(in_file):
        logger.error("Input file not found!")
        return set()
    logger.info("Counting document ids...")
    in_ids = count.get_document_ids(in_file)
    logger.info(f"{len(in_ids)} given, checking against database...")
    todo_ids = set()
    for ent_type in ent_types:
        todo_ids |= get_untagged_doc_ids_by_ent_type(collection, in_ids, ent_type, MetaDicTagger, logger)
    filter_and_sanitize(in_file, out_file, todo_ids, logger)
    return todo_ids


def add_doc_tagged_by_infos(document_ids: Set[int], collection: str, ent_types: List[str], tagger_name, tagger_version,
                            logger):
    # Add DocTaggedBy
    logger.info('Adding doc_tagged_by_info...')
    doc_tagged_by = []
    number_of_docs = len(document_ids)
    progress = Progress(total=number_of_docs * len(ent_types), print_every=1000, text="Compute insert...")
    progress.start_time()
    progress_i = 0
    for ent_type in ent_types:
        for doc_id in document_ids:
            progress_i += 1
            progress.print_progress(progress_i)
            doc_tagged_by.append(dict(
                document_id=doc_id,
                document_collection=collection,
                tagger_name=tagger_name,
                tagger_version=tagger_version,
                ent_type=ent_type,
                date_inserted=datetime.now()
            ))

    logger.info('Inserting...')
    session = Session.get()
    DocTaggedBy.bulk_insert_values_into_table(session, doc_tagged_by, check_constraints=True)
    logger.info('Finished')


def main(arguments=None):
    parser = ArgumentParser(description="Tag given documents in pubtator format and insert tags into database")

    parser.add_argument("-t", "--tag", choices=TAG_TYPE_MAPPING.keys(), nargs="+", default="DA")
    parser.add_argument("-c", "--collection", required=True)

    group_settings = parser.add_argument_group("Settings")
    group_settings.add_argument("--config", default=PREPROCESS_CONFIG,
                                help="Configuration file (default: {})".format(PREPROCESS_CONFIG))
    group_settings.add_argument("--loglevel", default="INFO")
    group_settings.add_argument("--workdir", default=None)
    group_settings.add_argument("--skip-load", action='store_true',
                                help="Skip bulk load of documents on start (expert setting)")

    group_settings.add_argument("-w", "--workers", default=1, help="Number of processes for parallelized preprocessing",
                                type=int)
    parser.add_argument("-y", "--yes_force", help="skip prompt for workdir deletion", action="store_true")

    parser.add_argument("input", help="composite pubtator file", metavar="IN_DIR")
    args = parser.parse_args(arguments)

    conf = Config(args.config)

    # create directories
    root_dir = root_dir = os.path.abspath(args.workdir) if args.workdir else tempfile.mkdtemp()
    log_dir = log_dir = os.path.abspath(os.path.join(root_dir, "log"))
    ext_in_file = args.input
    in_file = os.path.abspath(os.path.join(root_dir, "in.pubtator"))

    if args.workdir and os.path.exists(root_dir):
        if not args.yes_force:
            print(f"{root_dir} already exists, continue and delete?")
            resp = input("y/n")
            if resp not in {"y", "Y", "j", "J", "yes", "Yes"}:
                print("aborted")
                exit(0)
            else:
                shutil.rmtree(root_dir)
        else:
            shutil.rmtree(root_dir)
        # only create root dir if workdir is set
        os.makedirs(root_dir)
    # logdir must be created in both cases
    os.makedirs(log_dir)

    # create loggers
    logger = init_preprocess_logger(os.path.join(log_dir, "preprocessing.log"), args.loglevel.upper())
    init_sqlalchemy_logger(os.path.join(log_dir, "sqlalchemy.log"), args.loglevel.upper())
    logger.info(f"Project directory:{root_dir}")

    ent_types = DALL if "DA" in args.tag else [TAG_TYPE_MAPPING[x] for x in args.tag]
    document_ids = prepare_input(ext_in_file, in_file, logger, ent_types, args.collection)
    number_of_docs = len(document_ids)

    if number_of_docs == 0:
        logger.info('No documents to process - stopping')
        exit(1)

    if not args.skip_load:
        document_bulk_load(in_file, args.collection, logger=logger)
    else:
        logger.info("Skipping bulk load")

    kwargs = dict(collection=args.collection, root_dir=root_dir, input_dir=None, logger=logger,
                  log_dir=log_dir, config=conf, mapping_id_file=None, mapping_file_id=None)

    metafactory = PharmDictTaggerFactory(ent_types, kwargs)
    metatag = metafactory.create_MetaDicTagger()
    metatag.prepare()
    metatag.base_insert_tagger()

    session = Session.get()
    logger.info(f'Getting document ids from database for collection: {args.collection}...')
    document_ids_in_db = Document.get_document_ids_for_collection(session, args.collection)
    logger.info(f'{len(document_ids_in_db)} found')
    session.remove()

    def generate_tasks():
        for doc in read_pubtator_documents(in_file):
            t_doc = TaggedDocument(doc, ignore_tags=True)
            yield t_doc

    def do_task(in_doc: TaggedDocument):
        try:
            tagged_doc = metatag.tag_doc(in_doc)
            tagged_doc.clean_tags()
            return tagged_doc.tags
        except:
            logger.error('An error has occurred when tagging...')
            return []

    docs_done = multiprocessing.Value('i', 0)
    progress = Progress(total=number_of_docs, print_every=1000, text="Tagging...")
    progress.start_time()

    def consume_task(tags: List[TaggedEntity]):
        docs_done.value += 1
        progress.print_progress(docs_done.value)
        if len(tags) > 0:
            doc_id = tags[0].document
            if doc_id in document_ids_in_db and tags:
                metatag.base_insert_tags_partial(tags)

        if docs_done.value % BULK_INSERT_AFTER_K == 0:
            metatag.bulk_insert_partial_tags()

    def shutdown_consumer():
        metatag.bulk_insert_partial_tags()

    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    producer = ProducerWorker(task_queue, generate_tasks, args.workers)
    workers = [Worker(task_queue, result_queue, do_task) for n in range(args.workers)]
    consumer = ConsumerWorker(result_queue, consume_task, args.workers, shutdown=shutdown_consumer)

    producer.start()
    for w in workers:
        w.start()
    consumer.start()
    consumer.join()

    # Finally add doc tagged by infos
    document_ids = document_ids.intersection(document_ids_in_db)
    add_doc_tagged_by_infos(document_ids, args.collection, ent_types, metatag.__name__, metatag.__version__, logger)

    if not args.workdir:
        logger.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)

    progress.done()


if __name__ == '__main__':
    main()
