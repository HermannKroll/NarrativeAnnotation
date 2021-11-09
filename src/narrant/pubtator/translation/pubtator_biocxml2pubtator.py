import argparse
import glob

import logging

import bioc
import tarfile

import multiprocessing


from narrant.progress import Progress
from narrant.pubtator.document import TaggedDocument, TaggedEntity
from narrant.util.multiprocessing.ConsumerWorker import ConsumerWorker
from narrant.util.multiprocessing.ProducerWorker import ProducerWorker
from narrant.util.multiprocessing.Worker import Worker


def convert_pubtator_biocxml2pubtator(input_dir: str, output: str, workers=1, estimated_document_count=35000000):
    """
    Converts the PubTator Central Bioc XML Dump to a PubTator file
    :param input_dir: the directory of the dump (files must be stored in their .gz archives)
    :param output: Output PubTator file
    :param workers: The number of parallel workers
    :param estimated_document_count: the count of all documents to estimate the progress
    :return: None
    """
    progress = Progress(total=estimated_document_count, print_every=10000, text="Converting...")
    progress.start_time()

    def generate_tasks():
        logging.info('Counting files...')
        all_files = list(glob.glob(f'{input_dir}/**/BioCXML.*.gz', recursive=True))
        logging.info(f'Find {len(all_files)} files')
        for tar_file in all_files:
            yield tar_file

    f_out = open(output, 'wt')
    docs_done = multiprocessing.Value('i', 0)

    def consume_task(out_doc: TaggedDocument):
        docs_done.value += 1
        progress.print_progress(docs_done.value)
        f_out.write(str(out_doc) + '\n')

    # generator expression that takes a tar input file and yields all annotated PubTator documents
    def do_task(tar_input_file: str):
        with tarfile.open(tar_input_file) as tar_file:
            for member in tar_file.getmembers():
                member = tar_file.extractfile(member)
                # content = member.read()
                # read from a ByteIO
                reader = bioc.BioCXMLDocumentReader(member)
                collection_info = reader.get_collection_info()
                for document in reader:
                    try:
                        if document.passages:
                            if 'article-id_pmid' in document.passages[0].infons:
                                # convert pmcid id to pmid
                                document_id = int(document.passages[0].infons['article-id_pmid'])
                            else:
                                # its a pmid id
                                document_id = int(document.id)
                            title = document.passages[0].text
                            abstract = []
                            entities = []
                            for idx, passage in enumerate(document.passages):
                                # starts with ensures that abstract_titles as well as abstracts are exported
                                if "type" in passage.infons and passage.infons["type"] == "abstract":
                                    if passage.text.lower().startswith("citation"):
                                        break  # skip citations
                                    abstract.append(passage.text)
                                # is it a abstract section title?
                                elif "type" in passage.infons and passage.infons["type"] == "abstract_title_1":
                                    if passage.text.lower().startswith("citation"):
                                        break  # skip citations
                                    abstract.append(passage.text)
                                elif idx > 0:
                                    break  # no title, no abstract, do not care
                                if passage.annotations:
                                    for anno in passage.annotations:
                                        if "identifier" in anno.infons:
                                            ent_id = anno.infons["identifier"]
                                            ent_type = anno.infons["type"]
                                            ent_txt = anno.text
                                            for loc in anno.locations:
                                                ent_start = loc.offset
                                                ent_stop = loc.end
                                                ent_len = loc.end
                                                entities.append(TaggedEntity(document=document_id, start=ent_start,
                                                                             end=ent_stop, text=ent_txt,
                                                                             ent_type=ent_type,
                                                                             ent_id=ent_id))

                            abstract = ' '.join(abstract)
                            doc = TaggedDocument(title=title, abstract=abstract, id=document_id)
                            doc.tags = entities
                            doc.sort_tags()
                            doc.check_and_repair_tag_integrity()
                            yield doc
                    #  except ValueError:
                    #     logging.warning(f'Skip document because {ValueError}')
                    except KeyError:
                        logging.warning(f'Skip document because {KeyError}')

    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    producer = ProducerWorker(task_queue, generate_tasks, workers)
    workers = [Worker(task_queue, result_queue, do_task) for i in range(0, workers)]
    consumer = ConsumerWorker(result_queue, consume_task, workers)

    producer.start()
    for w in workers:
        w.start()
    consumer.start()
    consumer.join()
    f_out.close()

    progress.done()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output")
    parser.add_argument("-w", "--workers", type=int, help="Amount of parallel workers")
    parser.add_argument("-c", "--collection", required=True, help="Document collection name")
    parser.add_argument("--logsql", action="store_true", help='logs sql statements')
    args = parser.parse_args()

    if args.logsql:
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S',
                            level=logging.INFO)

    convert_pubtator_biocxml2pubtator(args.input_dir, args.output, args.workers)


if __name__ == "__main__":
    main()
