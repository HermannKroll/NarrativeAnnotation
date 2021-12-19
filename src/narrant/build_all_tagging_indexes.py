import logging

from narrant.config import PREPROCESS_CONFIG
from narrant.preprocessing.pharmacy.pharmdicttagger import PharmDictTagger


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    kwargs = dict(logger=logging, config=PREPROCESS_CONFIG, collection="Test")

    for ent_type, tagger_class in PharmDictTagger.tagger_by_type.items():
        logging.info(f'Init tagger for type: {ent_type}')
        tagger = tagger_class(**kwargs)
        tagger.prepare()


if __name__ == "__main__":
    main()
