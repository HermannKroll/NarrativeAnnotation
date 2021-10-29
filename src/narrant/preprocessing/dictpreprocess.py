import logging
import multiprocessing
import os
import shutil
import tempfile
from argparse import ArgumentParser
from datetime import datetime
from typing import Iterable

from narrant.backend.database import Session
from narrant.backend.load_document import document_bulk_load
from narrant.config import PREPROCESS_CONFIG
from narrant.preprocessing.config import Config
from narrant.preprocessing.enttypes import TAG_TYPE_MAPPING, DALL
from narrant.preprocessing.preprocess import init_preprocess_logger, init_sqlalchemy_logger, \
    get_untagged_doc_ids_by_ent_type
from narrant.preprocessing.tagging.metadictagger import MetaDicTagger, MetaDicTaggerFactory
from narrant.progress import print_progress_with_eta
from narrant.pubtator import count
from narrant.pubtator.document import TaggedDocument
from narrant.pubtator.extract import read_pubtator_documents
from narrant.pubtator.sanitize import filter_and_sanitize
from narrant.util.multiprocessing.ConsumerWorker import ConsumerWorker
from narrant.util.multiprocessing.ProducerWorker import ProducerWorker
from narrant.util.multiprocessing.Worker import Worker


def prepare_input(in_file: str, out_file: str, logger: logging.Logger, ent_types: Iterable[str],
                  collection: str) -> int:
    if not os.path.exists(in_file):
        logger.error("Input file not found!")
        return False
    logger.info("Counting document ids...")
    in_ids = count.get_document_ids(in_file)
    logger.info(f"{len(in_ids)} given, checking against database...")
    todo_ids = set()
    for ent_type in ent_types:
        todo_ids |= get_untagged_doc_ids_by_ent_type(collection, in_ids, ent_type, MetaDicTagger, logger)
    filter_and_sanitize(in_file, out_file, todo_ids, logger)
    return len(todo_ids)


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
        # only create root dir if workdir is set
        os.makedirs(root_dir)
    # logdir must be created in both cases
    os.makedirs(log_dir)

    # create loggers
    logger = init_preprocess_logger(os.path.join(log_dir, "preprocessing.log"), args.loglevel.upper())
    init_sqlalchemy_logger(os.path.join(log_dir, "sqlalchemy.log"), args.loglevel.upper())
    logger.info(f"Project directory:{root_dir}")

    ent_types = DALL if "DA" in args.tag else [TAG_TYPE_MAPPING[x] for x in args.tag]
    number_of_docs = prepare_input(ext_in_file, in_file, logger, ent_types, args.collection)

    if not number_of_docs:
        logger.info('No documents to process - stopping')
        exit(1)

    if not args.skip_load:
        document_bulk_load(in_file, args.collection, logger=logger)
    else:
        logger.info("Skipping bulk load")

    kwargs = dict(collection=args.collection, root_dir=root_dir, input_dir=None, logger=logger,
                  log_dir=log_dir, config=conf, mapping_id_file=None, mapping_file_id=None)

    metafactory = MetaDicTaggerFactory(ent_types, kwargs)
    metatag = metafactory.create_MetaDicTagger()
    metatag.prepare()
    metatag.base_insert_tagger()

    def generate_tasks():
        for doc in read_pubtator_documents(in_file):
            t_doc = TaggedDocument(doc, ignore_tags=True)
            if t_doc.title:  # or t_doc.abstract:
                yield t_doc

    def do_task(in_doc: TaggedDocument):
        tagged_doc = metatag.tag_doc(in_doc)
        tagged_doc.clean_tags()
        return tagged_doc

    docs_done = multiprocessing.Value('i', 0)
    docs_to_do = multiprocessing.Value('i', number_of_docs)
    start = datetime.now()

    def consume_task(out_doc: TaggedDocument):
        docs_done.value += 1
        print_progress_with_eta("Tagging...", docs_done.value, docs_to_do.value, start, print_every_k=1000,
                                logger=logger)
        if out_doc.tags:
            metatag.base_insert_tags(out_doc, auto_commit=False)

        if docs_done.value % 10000 == 0:
            Session.get().commit()

    def shutdown_consumer():
        Session.get().commit()

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
    logger.info(f"finished in {(datetime.now() - start).total_seconds()} seconds")

    if not args.workdir:
        logger.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)


if __name__ == '__main__':
    main()
