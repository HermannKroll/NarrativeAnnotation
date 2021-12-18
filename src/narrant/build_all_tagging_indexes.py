import logging

from narrant.config import PREPROCESS_CONFIG
from narrant.preprocessing.tagging.metadictagger import PharmDictTagger


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    kwargs = dict(collection="Test", root_dir=None, input_dir=None, logger=logging,
                  log_dir=None, config=PREPROCESS_CONFIG, mapping_id_file=None, mapping_file_id=None)

    for ent_type, tagger_class in PharmDictTagger.tagger_by_type.items():
        logging.info(f'Init tagger for type: {ent_type}')
        tagger = tagger_class(**kwargs)
        tagger.prepare()


if __name__ == "__main__":
    main()
