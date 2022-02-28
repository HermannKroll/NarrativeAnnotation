import hashlib
import itertools as it
import os
import pickle
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import List

from narrant.config import TMP_DIR, DICT_TAGGER_BLACKLIST, TMP_DIR_TAGGER
from narrant.preprocessing.tagging.base import BaseTagger
from kgextractiontoolbox.document.document import TaggedDocument, TaggedEntity


class DictIndex:

    def __init__(self, source_md5_sum, tagger_version):
        self.source_md5_sum, self.tagger_version = source_md5_sum, tagger_version
        self.desc_by_term = {}

    def has_md5_sum(self):
        if "source_md5_sum" in self.__dict__:
            return True
        else:
            return False


def get_n_tuples(in_list, n):
    if n == 0:
        return []
    for i, element in enumerate(in_list):
        if i + n <= len(in_list):
            yield in_list[i:i + n]
        else:
            break


def clean_vocab_word_by_split_rules(word: str) -> str:
    if word and re.match(r"[^\w]", word[0]):
        word = word[1:]
    if word and re.match(r"[^\w]", word[-1]):
        word = word[:-1]
    return word


def split_indexed_words(content):
    words = content.split(' ')
    ind_words = []
    next_index_word = 0
    for word in words:
        ind = next_index_word
        word_offset = 0
        while word and re.match(r"[^\w]", word[0]):
            word = word[1:]
            ind += 1
            word_offset += 1
        while word and re.match(r"[^\w]", word[-1]):
            word = word[:-1]
            word_offset += 1
        ind_words.append((word, ind))

        # index = last index + length of last word incl. offset
        next_index_word = next_index_word + len(word) + word_offset + 1

    # For cases like "water-induced" add "water"
    amendment = []
    for word, index in ind_words:
        split = word.split("-")
        if len(split) == 2 and split[1][-2:] in {"ed", "et"}:
            amendment.append((split[0], index))
    ind_words += amendment
    return ind_words


class DictTagger(BaseTagger, metaclass=ABCMeta):
    PROGRESS_BATCH = 10000
    __name__ = None
    __version__ = None

    def __init__(self, short_name, long_name, version, tag_types, source, logger,
                 config, collection):
        super().__init__(config=config, collection=collection, logger=logger)
        self.tag_types = [tag_types, ]
        self.short_name, self.long_name, self.version = short_name, long_name, version
        self.index_cache = os.path.join(TMP_DIR_TAGGER, f'{short_name}_index.pkl')
        self.source = source
        self.desc_by_term = {}

    def get_types(self):
        return self.tag_types

    @staticmethod
    def get_md5_hash_from_content(path):
        """
        Gets the md5hash sum from the given path
        either it is a file and the file content is considered
        or it must be a directory and then the content of all files is considered
        :param path: path directory or file
        :return: md5sum of content
        """
        if os.path.isfile(path):
            hash_md5 = hashlib.md5()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        elif os.path.isdir(path):
            hash_md5 = hashlib.md5()
            for file in os.listdir(path):
                file = os.path.join(path, file)
                with open(file, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
            return hash_md5.hexdigest()
        else:
            raise ValueError(f'{path} must either be a directory or file')

    def _index_from_pickle(self):
        if os.path.isfile(self.index_cache):
            with open(self.index_cache, 'rb') as f:
                index = pickle.load(f)
                if not isinstance(index, DictIndex):
                    self.logger.warning('Ignore index: expect index file to contain an IndexObject: {}'
                                        .format(self.index_cache))
                    return None

                if not index.has_md5_sum():
                    self.logger.warning('Ignore index: md5 hash was not computed before')
                    return None

                if index.tagger_version != self.version:
                    self.logger.warning('Ignore index: index does not match tagger version ({} index vs. {} tagger)'
                                        .format(index.tagger_version, self.version))
                    return None

                md5sum_now = DictTagger.get_md5_hash_from_content(self.source)
                md5sum_before = DictTagger.get_md5_hash_from_content(index.source_md5_sum)
                if md5sum_now != md5sum_before:
                    self.logger.warning('Ignore index: md5 sums of sources differ - recreating index')
                    return None

                self.logger.debug('Use pre-computed index from {}'.format(self.index_cache))
                self.desc_by_term = index.desc_by_term
                return index
        pass

    def _index_to_pickle(self):
        index = DictIndex(self.source, self.version)
        index.desc_by_term = self.desc_by_term
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)
        self.logger.debug('Storing Index cache to: {}'.format(self.index_cache))
        pickle.dump(index, open(self.index_cache, 'wb+'))

    @abstractmethod
    def _index_from_source(self):
        pass

    @staticmethod
    def get_blacklist_set():
        with open(DICT_TAGGER_BLACKLIST) as f:
            blacklist = f.read().splitlines()
        blacklist_set = set()
        for s in blacklist:
            s_lower = s.lower().strip()
            blacklist_set.add(s_lower)
            blacklist_set.add('{}s'.format(s_lower))
            blacklist_set.add('{}e'.format(s_lower))
            if s_lower.endswith('s') or s_lower.endswith('e'):
                blacklist_set.add(s_lower[0:-1])
        return blacklist_set

    def prepare(self):
        if self._index_from_pickle():
            self.logger.info(f'{self.long_name} initialized from cache '
                             f'({len(self.desc_by_term.keys())} term mappings) - ready to start')
        else:
            self._index_from_source()
            blacklist_set = DictTagger.get_blacklist_set()
            self.desc_by_term = {k.lower().strip(): v for k, v in self.desc_by_term.items() if
                                 k.lower().strip() not in blacklist_set}
            self._index_to_pickle()

    def tag_doc(self, in_doc: TaggedDocument) -> TaggedDocument:
        """
        Generate tags for a TaggedDocument
        :param in_doc: document containing title+abstract to tag. Is modified by adding tags
        :return: the modified in_doc
        """
        and_check_range = 5
        connector_words = {"and", "or"}
        abb_vocab = dict()
        out_doc = in_doc
        pmid, title, abstact = in_doc.id, in_doc.title, in_doc.abstract
        content = title.strip() + " " + abstact.strip()
        content = content.lower()

        # split into indexed single words
        ind_words = split_indexed_words(content)

        tags = []
        for spaces in range(self.config.dict_max_words):
            for word_tuple in get_n_tuples(ind_words, spaces + 1):
                hits = self.get_hits(word_tuple, pmid)
                tags += hits

                if self.config.custom_abbreviations and hits:
                    words, indexes = zip(*word_tuple)
                    # only learn abbreviations from full entity mentions
                    term = " ".join(words)
                    if len(term) >= self.config.dict_min_full_tag_len:
                        match = re.match(r" \(([^\(\)]*)\).*", content[indexes[-1] + len(words[-1]):])
                        if match:
                            # strip the abbreviation
                            abbreviation = match.groups()[0].strip()
                            abb_vocab[abbreviation] = [(t.ent_type, t.ent_id) for t in hits]

        if abb_vocab:
            for spaces in range(self.config.dict_max_words):
                for word_tuple in get_n_tuples(ind_words, spaces + 1):
                    tags += self.get_hits(word_tuple, pmid, abb_vocab)

        if self.config.dict_check_abbreviation:
            tags = DictTagger.clean_abbreviation_tags(tags, self.config.dict_min_full_tag_len)

        out_doc.tags += tags
        return out_doc

    def get_hits(self, word_tuple, pmid, abb_vocab=None):
        words, indexes = zip(*word_tuple)
        term = " ".join(words)
        if not term:
            return []
        start = indexes[0]
        end = indexes[-1] + len(words[-1])
        hits = list(self.generate_tagged_entities(end, pmid, start, term, tmp_vocab=abb_vocab))
        return hits

    connector_words = {"and", "or"}

    @staticmethod
    def conjunction_product(token_seq, seperated=False):
        """
        split token_seq at last conn_word, return product of all sub token sequences. Exclude connector words.
        :param seperated: return left_tuples, right_tuples instead of left_tuples+right_tuples
        """
        cwords_indexes = [n for n, (w, i) in enumerate(token_seq) if w in DictTagger.connector_words]

        if not cwords_indexes:  # or max(cwords_indexes) in [0, len(token_seq)-1]:
            return []
        left = token_seq[:max(cwords_indexes)]
        right = token_seq[max(cwords_indexes):]

        left = [(w, i) for w, i in left if w not in DictTagger.connector_words]
        right = [(w, i) for w, i in right if w not in DictTagger.connector_words]

        left_tuples = [[]] + [t for n in range(0, len(left) + 1) for t in list(get_n_tuples(left, n))]
        right_tuples = [[]] + [t for n in range(0, len(right) + 1) for t in list(get_n_tuples(right, n))]
        yield from [(lt, rt) for lt, rt in it.product(left_tuples, right_tuples) if lt + rt]

    def _tag(self, in_file, out_file):
        with open(in_file) as f:
            document = f.read()
        result = self.tag_doc(TaggedDocument(document))
        with open(out_file, "w+") as f:
            f.write(str(result))

    def generate_tag_lines(self, end, pmid, start, term):
        hits = self._get_term(term)
        # print(f"Found {hits} for '{term}'")
        if hits:
            for desc in hits:
                yield pmid, start, end, term, self.tag_types[0], desc

    def generate_tagged_entities(self, end, pmid, start, term, tmp_vocab=None):
        hits = set()
        if tmp_vocab:
            tmp_hit = tmp_vocab.get(term)
            if tmp_hit:
                hits |= {hit[1] for hit in tmp_hit}
        else:
            hits |= set(self._get_term(term))

        # print(f"Found {hits} for '{term}'")
        if hits:
            for desc in hits:
                yield TaggedEntity((pmid, start, end, term, self.tag_types[0], desc))

    def _get_term(self, term):
        hits = self.desc_by_term.get(term)
        return hits if hits else set()

    @staticmethod
    def clean_abbreviation_tags(tags: List[TaggedEntity], minimum_tag_len=5):
        """
        This method removes all tags which are assumed to be an abbreviation and which do not have a long expression
        within the document
        e.g. Aspirin (ASA) -> ASA is allowed in the document because Aspirin is associated with the same descriptor
        without aspirin ASA will further not be kept as a valid tag
        :param minimum_tag_len: the minimum tag length to treat a term as a 'full' tag
        :param tags: a list of tags
        :return: a list of cleaned tags
        """
        tags_cleaned = []
        desc2tags = defaultdict(list)
        for t in tags:
            desc2tags[t.ent_id].append(t)

        # search if a full tag is found for a descriptor
        for desc, tags in desc2tags.items():
            keep_desc = False
            for t in tags:
                if len(t.text) >= minimum_tag_len:
                    keep_desc = True
                    break
            if keep_desc:
                tags_cleaned.extend(tags)
        return tags_cleaned
