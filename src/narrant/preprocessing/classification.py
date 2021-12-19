import multiprocessing
import os
import shutil
import tempfile
from argparse import ArgumentParser

from narrant.backend.database import Session
from narrant.backend.load_document import document_bulk_load
from narrant.backend.models import DocumentClassification, Document
from narrant.config import PREPROCESS_CONFIG
from narrant.preprocessing.classifier import Classifier
from narrant.preprocessing.dictpreprocess import prepare_input
from narrant.preprocessing.preprocess import init_preprocess_logger, init_sqlalchemy_logger
from narrant.progress import Progress
from narrant.pubtator.document import TaggedDocument
from narrant.pubtator.extract import read_pubtator_documents
from narrant.util.multiprocessing.ConsumerWorker import ConsumerWorker
from narrant.util.multiprocessing.ProducerWorker import ProducerWorker
from narrant.util.multiprocessing.Worker import Worker


def main(arguments=None):
    parser = ArgumentParser(description="Tag given documents in pubtator format and insert tags into database")

    parser.add_argument("-c", "--collection", required=True)
    parser.add_argument("-r", "--ruleset", required=True)
    parser.add_argument("--cls", required=True)

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

    parser.add_argument("-i", "--input", required=False, help="composite pubtator file", metavar="IN_DIR")
    args = parser.parse_args(arguments)

    # create directories
    root_dir = os.path.abspath(args.workdir) if args.workdir else tempfile.mkdtemp()
    log_dir = os.path.abspath(os.path.join(root_dir, "log"))
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

    input_file_given = True
    if args.input:
        document_ids = prepare_input(ext_in_file, in_file, logger, args.collection)
        number_of_docs = len(document_ids)

        if number_of_docs == 0:
            logger.info('No documents to process - stopping')
            exit(1)

        if not args.skip_load:
            document_bulk_load(in_file, args.collection, logger=logger)
        else:
            logger.info("Skipping bulk load")
    else:
        input_file_given = False
        logger.info('No input file given')
        logger.info(f'Counting documents for collection: {args.collection}')
        session = Session.get()
        number_of_docs = Document.count_documents_in_collection(session, args.collection)
        session.remove()

    classifier = Classifier(classification=args.cls, rule_path=args.ruleset)
    session = Session.get()

    def generate_tasks():
        if input_file_given:
            for doc in read_pubtator_documents(in_file):
                t_doc = TaggedDocument(doc, ignore_tags=True)
                if t_doc and t_doc.has_content():
                    yield t_doc
        else:
            db_session = Session.get()
            logger.info('Retrieving documents from database...')
            for doc in Document.iterate_over_documents_in_collection(db_session, args.collection):
                if doc.has_content():
                    yield doc
            db_session.remove()

    def do_task(in_doc: TaggedDocument):
        classifier.classify_document(in_doc)
        return in_doc

    docs_done = multiprocessing.Value('i', 0)
    progress = Progress(total=number_of_docs, print_every=1000, text="Classifying...")
    progress.start_time()

    def consume_task(out_doc: TaggedDocument):
        docs_done.value += 1
        progress.print_progress(docs_done.value)
        if out_doc.classification:
            for cls, rsn in out_doc.classification.items():
                rsn = rsn.replace("\\b", "").replace("\\w*", "*")
                DocumentClassification.bulk_insert_values_into_table(session, [{
                    "document_id": out_doc.id,
                    "document_collection": args.collection,
                    "classification": cls,
                    "explanation": rsn
                }])

    def shutdown_consumer():
        pass

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

    if not args.workdir:
        logger.info(f'Remove temp directory: {root_dir}')
        shutil.rmtree(root_dir)

    progress.done()


if __name__ == '__main__':
    main()
