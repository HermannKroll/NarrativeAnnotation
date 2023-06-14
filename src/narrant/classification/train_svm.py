import logging
from argparse import ArgumentParser

from narrant.classification.SVMClassifier import SVMClassifier


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    parser = ArgumentParser(description="Train a SVM based on a set of document ids")
    parser.add_argument("id_file", help="Input document id file (a document id per line)")
    parser.add_argument("model_file", help="File the model will be written to")
    parser.add_argument("-c", "--collection", help="Document collection the ids belong to", required=True)
    parser.add_argument("-s", "--samplesize", help="How many documents should be used for training", type=int,
                        required=True)
    parser.add_argument("-w", "--workers", help="How workers should be used for training (-1 = all cores, default)",
                        type=int, default=-1)

    args = parser.parse_args()
    SVMClassifier.train_model(document_id_file=args.id_file, document_collection=args.collection,
                              model_path=args.model_file, train_sample_size=args.samplesize, no_workers=args.workers)


if __name__ == "__main__":
    main()
