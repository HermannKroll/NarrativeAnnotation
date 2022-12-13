from argparse import ArgumentParser

from kgextractiontoolbox.entitylinking.classification import add_classification_args, perform_classification
from narrant.classification.SVMClassifier import SVMClassifier


def main(arguments=None):
    parser = ArgumentParser(description="Classification script")
    parser.add_argument("svm_model", help="Path to the trained SVM model")
    add_classification_args(parser)
    args = parser.parse_args(arguments)

    classifier = SVMClassifier(classification=args.cls, model_path=args.svm_model)
    perform_classification(classifier=classifier, document_collection=args.collection,
                           input_file=args.input, workdir=args.workdir, workers=args.workers,
                           consider_sections=args.sections, loglevel=args.loglevel, skip_load=args.skip_load,
                           force=args.yes_force)


if __name__ == '__main__':
    main()
