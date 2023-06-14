import hashlib
import os
import pickle
from abc import abstractmethod

from kgextractiontoolbox.entitylinking.tagging.dictagger import DictTagger
from narrant.config import TMP_DIR_TAGGER, DICT_TAGGER_BLACKLIST


class DictIndex:

    def __init__(self, source_md5_sum, tagger_version):
        self.source_md5_sum, self.tagger_version = source_md5_sum, tagger_version
        self.desc_by_term = {}

    def has_md5_sum(self):
        if "source_md5_sum" in self.__dict__:
            return True
        else:
            return False


class IndexedDictTagger(DictTagger):
    def __init__(self, short_name, long_name, version, tag_types, source, logger, config, collection,
                 tmp_dir=TMP_DIR_TAGGER, blacklist_file=DICT_TAGGER_BLACKLIST):
        super().__init__(short_name, long_name, version, tag_types, logger, config, collection,
                         blacklist_file=blacklist_file)
        self.index_cache = os.path.join(tmp_dir, f'{short_name}_index.pkl')
        self.source = source

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
            try:
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

                    md5sum_now = IndexedDictTagger.get_md5_hash_from_content(self.source)
                    md5sum_before = IndexedDictTagger.get_md5_hash_from_content(index.source_md5_sum)
                    if md5sum_now != md5sum_before:
                        self.logger.warning('Ignore index: md5 sums of sources differ - recreating index')
                        return None

                    self.logger.debug('Use pre-computed index from {}'.format(self.index_cache))
                    self.desc_by_term = index.desc_by_term
                    return index
            except ModuleNotFoundError:
                # Old index code was loaded
                return None
        pass

    def _index_to_pickle(self):
        index = DictIndex(self.source, self.version)
        index.desc_by_term = self.desc_by_term
        self.logger.debug('Storing Index cache to: {}'.format(self.index_cache))
        pickle.dump(index, open(self.index_cache, 'wb+'))

    @abstractmethod
    def _index_from_source(self):
        pass

    def prepare(self):
        if self._index_from_pickle():
            self.logger.info(f'{self.long_name} initialized from cache '
                             f'({len(self.desc_by_term.keys())} term mappings) - ready to start')
        else:
            self._index_from_source()
            super().prepare()
            self._index_to_pickle()
