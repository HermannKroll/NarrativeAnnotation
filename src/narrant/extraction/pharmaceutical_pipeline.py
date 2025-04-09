import argparse
import logging

from kgextractiontoolbox.config import NLP_CONFIG
from kgextractiontoolbox.extraction.pipeline import invoke_pipeline_start
from kgextractiontoolbox.extraction.versions import PATHIE_EXTRACTION, OPENIE_EXTRACTION, PATHIE_STANZA_EXTRACTION, \
    OPENIE6_EXTRACTION, OPENIE51_EXTRACTION, COSENTENCE_EXTRACTION
from narrant.extraction.loading.clean_load_genes import clean_and_translate_gene_ids

DOCUMENTS_TO_PROCESS_IN_ONE_BATCH = 500000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--idfile", help="Document ID file (documents must be in database)")
    parser.add_argument("-et", "--extraction_type", required=True, help="the extraction method",
                        choices=list(
                            [OPENIE_EXTRACTION, OPENIE51_EXTRACTION, OPENIE6_EXTRACTION, PATHIE_EXTRACTION,
                             PATHIE_STANZA_EXTRACTION, COSENTENCE_EXTRACTION]))
    parser.add_argument("-c", "--collection", required=True, help="Name of the given document collection")
    parser.add_argument("--config", help="OpenIE / PathIE Configuration file", default=NLP_CONFIG)
    parser.add_argument("-w", "--workers", help="number of parallel workers", default=1, type=int)
    parser.add_argument("-bs", "--batch_size",
                        help="Batch size (how many documents should be processed and loaded in a batch)",
                        default=DOCUMENTS_TO_PROCESS_IN_ONE_BATCH, type=int)
    parser.add_argument('--relation_vocab', default=None, help='Path to a relation vocabulary (json file)')
    parser.add_argument("--sections", action="store_true", default=False,
                        help="Should the section texts be considered in the extraction step?")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    invoke_pipeline_start(relation_vocab_path=args.relation_vocab, idfile=args.idfile, collection=args.collection,
                          extraction_type=args.extraction_type, batch_size=args.batch_size, workers=args.workers,
                          config=args.config, sections=args.sections, cleaning_function=clean_and_translate_gene_ids)


if __name__ == "__main__":
    main()
