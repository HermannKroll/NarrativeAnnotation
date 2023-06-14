from kgextractiontoolbox.document.document import TaggedDocument
from narrant import config
from narrant.preprocessing import enttypes
from narrant.preprocessing.enttypes import HEALTH_STATUS
from narrant.preprocessing.tagging.indexed_dictagger import IndexedDictTagger
from narrant.vocabularies.healthstatus_vocabulary import HealthStatusVocabulary

from nltk import pos_tag, word_tokenize


class HealthStatusTagger(IndexedDictTagger):
    TYPES = (enttypes.HEALTH_STATUS,)
    __name__ = "HealthStatusTagger"
    __version__ = "1.0.0"

    def __init__(self, *args, **kwargs):
        super().__init__("healthstatus", "HealthStatusTagger", HealthStatusTagger.__version__,
                         enttypes.HEALTH_STATUS, config.HEALTH_STATUS_TAGGER_VOCAB_DIRECTORY,
                         *args, **kwargs)

    def _index_from_source(self):
        self.logger.info('Creating dictionary from source...')
        self.desc_by_term = HealthStatusVocabulary.create_health_status_vocabulary()
        self.logger.info(f'{len(self.desc_by_term)} Health Status terms found in database')

    def custom_tag_filter_logic(self, in_doc: TaggedDocument):
        hs_tags = list([x for x in in_doc.tags if x.ent_type == HEALTH_STATUS])
        if len(hs_tags) == 0:
            return

        # reduce text by index of first and last token (+-25 chars if possible)
        abstract = in_doc.get_text_content()
        abs_min = max(min([t.start for t in hs_tags]) - 25, 0)
        abs_max = min(max([t.end for t in hs_tags]) + 25, len(abstract) - 1)

        if abs(abs_max - abs_min) == 0:
            # empty text span - Stop here
            in_doc.tags = [t for t in in_doc.tags if t.ent_type != HEALTH_STATUS]
            return

        # get noun tags from abstract. select only nouns, plural forms and proper nouns
        try:
            text_tkns = word_tokenize(abstract[abs_min:abs_max].strip(" ,.!?;'`-_+*~\"%&/\\"))
            noun_tags = set([x[0] for x in pos_tag(text_tkns) if x[1] in {'NN', 'NNS', 'NNP', 'NNPS'}])

            # keep tags only if they are nouns (keep normal + filtered health status)
            filtered_hs = [x for x in hs_tags if x.text in noun_tags]
            in_doc.tags = [t for t in in_doc.tags if t.ent_type != HEALTH_STATUS] + filtered_hs
        except IndexError:
            # IF NLTK stops working
            in_doc.tags = [t for t in in_doc.tags if t.ent_type != HEALTH_STATUS]

