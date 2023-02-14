import json
import logging
import os
import string

from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.config import TARGET_TAGGER_VOCAB_DIRECTORY, TARGET_TAGGER_VOCAB
from narrant.preprocessing.enttypes import TARGET
from narrant.vocabularies.chembl_vocabulary import ChemblVocabulary
from narrant.vocabularies.generic_vocabulary import GenericVocabulary

URL = "https://www.ebi.ac.uk"
URL_PATH = "/chembl/api/data/target?format=json&limit={}"


class TargetVocabulary(ChemblVocabulary):

    def __init__(self, vocab_file=TARGET_TAGGER_VOCAB, entity_type=TARGET, entity_type_in_vocab=TARGET):
        super().__init__(vocab_file, entity_type)
        self.ignored_target_types = {'organism', 'tissue', 'unchecked', 'no target'}
        self.allowed_target_types = {}
        self.allowed_organism = {}
        self.entity_type_in_vocab = entity_type_in_vocab
        self.preferred_target_organism = "homo sapiens"

    @staticmethod
    def create_target_vocabulary(expand_by_s_and_e=True):
        if not os.path.isfile(TARGET_TAGGER_VOCAB):
            TargetVocabulary().initialize_vocabulary()

        return GenericVocabulary.create_vocabulary_from_directory(TARGET_TAGGER_VOCAB_DIRECTORY,
                                                                  expand_terms=expand_by_s_and_e)

    def _create_vocabulary_from_dir(self, tmp_dir):
        vocabulary = Vocabulary('')

        logging.info("Start creating target vocabulary.")
        target2organism = {}
        target2entry = {}
        term2targets = {}
        target2no_of_synonyms = {}

        for file_name in os.listdir(tmp_dir):
            file_name = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_name):
                continue

            with open(file_name) as file:
                for t in json.load(file):
                    if not (t['target_chembl_id'] or t['component_description']):
                        continue
                    # ignore certain target types
                    if len(self.ignored_target_types) > 0 \
                            and t["target_type"].strip().lower() in self.ignored_target_types:
                        continue
                    # if certain types are allowed, check type
                    if len(self.allowed_target_types) > 0 \
                            and t["target_type"].strip().lower() not in self.allowed_target_types:
                        continue

                    # Ignore targets if they belong to an organism that is not desired
                    if len(self.allowed_organism) > 0 and 'organism' in t:
                        if t["organism"] and t["organism"].strip().lower() not in self.allowed_organism:
                            continue
                        # otherwise organism not known -> continue

                    entity_id = t['target_chembl_id']
                    heading = t['pref_name']
                    if 'organism' in t and t["organism"]:
                        organism = t["organism"].strip().lower()
                    else:
                        organism = "unknown organism"
                    target2organism[entity_id] = organism

                    synonyms = list()
                    if t['target_components']:
                        for tc in t['target_components']:
                            if tc['component_description']:
                                synonyms.append(tc['component_description'])
                            if tc['target_component_synonyms']:
                                synonyms.extend([syn['component_synonym'] for syn in tc['target_component_synonyms']])

                    target2entry[entity_id] = (heading, synonyms)
                    target2no_of_synonyms[entity_id] = len(synonyms)
                    for term in [heading] + synonyms:
                        term = term.strip().lower()
                        if term in term2targets:
                            term2targets[term].add(entity_id)
                        else:
                            term2targets[term] = {entity_id}

        logging.info('Computing vocabulary...')
        heading2synonyms = {}
        heading2best_heading = {}
        trans_map = {p: '' for p in string.punctuation}
        translator = str.maketrans(trans_map)
        for entity_id in target2entry:
            heading, synonyms = target2entry[entity_id]
            heading_l = heading.lower().translate(translator).strip()
            if heading_l in heading2synonyms:
                h_old = sum([1 for c in heading2best_heading[heading_l] if c.isupper()])
                h_new = sum([1 for c in heading if c.isupper()])
                if h_new > h_old:
                    heading2best_heading[heading_l] = heading
                heading2synonyms[heading_l].update(synonyms)
            else:
                heading2best_heading[heading_l] = heading
                heading2synonyms[heading_l] = set(synonyms)

        for heading_l, synonyms in heading2synonyms.items():
            heading = heading2best_heading[heading_l]
            vocabulary.add_vocab_entry(heading, self.entity_type_in_vocab, heading, ";".join(synonyms))

       #  for entity_id in target2entry:
       #      heading, synonyms = target2entry[entity_id]
       #      # If this target belongs to humans, everything is fine
       #    #  if target2organism[entity_id] == self.preferred_target_organism:
       #  #        vocabulary.add_vocab_entry(entity_id, self.entity_type_in_vocab, heading, ";".join(synonyms))
       # #     else:
       #      # Search whether the term already refers to a human target
       #      # if so, just keep the human target (preferred one)
       #      # if not, prefer target with more synonyms
       #      add_target = True
       #      for term in synonyms + [heading]:
       #          term = term.strip().lower()
       #          possible_target_ids = list([t for t in term2targets[term] if t != entity_id])
       #          # if we have several options for that term
       #          if len(possible_target_ids) > 0:
       #              organisms = list([target2organism[t] for t in possible_target_ids])
       #              # if some other has a human organism - take this
       #              if self.preferred_target_organism in organisms \
       #                      and target2organism[entity_id] != self.preferred_target_organism:
       #                  add_target = False
       #                  break
       #
       #              current_syn_no = target2no_of_synonyms[entity_id]
       #              min_syn_no = min([target2no_of_synonyms[t] for t in possible_target_ids])
       #              # if some other has more synonyms
       #              if current_syn_no < min_syn_no:
       #                  add_target = False
       #                  break
       #              # same number of synonyms
       #              elif current_syn_no == min_syn_no:
       #                  possible_target_ids = sorted(possible_target_ids, key=lambda x: len(x))
       #                  # take the lowest one in alphanumerical order
       #                  if len(entity_id) > len(possible_target_ids[0]):
       #                      add_target = False
       #                      break
       #                  elif len(entity_id) == len(possible_target_ids[0]) and entity_id > possible_target_ids[0]:
       #                      add_target = False
       #                      break
       #                  # Otherwise you can take it

          #  if add_target:
          #      vocabulary.add_vocab_entry(entity_id, self.entity_type_in_vocab, heading, ";".join(synonyms))

        logging.info("Parsed {} targets with {} terms. Saving vocabulary..."
                     .format(vocabulary.count_distinct_entities(),
                             vocabulary.count_distinct_terms()))

        vocabulary.export_vocabulary_as_tsv(self.vocab_dir)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)

    TargetVocabulary().initialize_vocabulary(force_create=True)
