import logging
import os
import shutil

from narrant.config import PREPROCESS_CONFIG, TMP_DIR_TAGGER
from narrant.preprocessing.pharmacy.pharmdicttagger import PharmDictTagger


def build_tagging_indexes():
    logging.info('=='*60)
    logging.info('Building Tagging Indexes')
    logging.info('==' * 60)
    kwargs = dict(logger=logging, config=PREPROCESS_CONFIG, collection="Test")
    if os.path.exists(TMP_DIR_TAGGER) and os.path.isdir(TMP_DIR_TAGGER):
        shutil.rmtree(TMP_DIR_TAGGER)
        os.makedirs(TMP_DIR_TAGGER)

    for ent_type, tagger_class in PharmDictTagger.tagger_by_type.items():
        logging.info(f'Init tagger for type: {ent_type}')
        tagger = tagger_class(**kwargs)
        tagger.prepare()
    logging.info('==' * 60)


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    build_tagging_indexes()


if __name__ == "__main__":
    main()
