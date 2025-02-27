import gzip
import json
import logging
from itertools import islice

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import EntityResolverData
from narrant.config import GENE_FILE


class GeneMapper:
    """
    important note: human taxonomy id is '9606'. Composition of components in GENE_FILE:
    components[0] = tax_id, components[1] = gene_id, components[2] = gene name
    """
    NAME = "GeneMapper"

    HUMAN_SPECIES_ID = '9606'

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.human_gene_dict = {}
        self.gene_to_human_id_dict = {}
        self.load_index()

    def _build_human_gene_name_dict(self, gene_file=GENE_FILE):
        """
        used in build_gene_id_dict() for mapping gene names to human gene ids
        :param gene_file:
        """
        self.human_gene_dict.clear()
        with gzip.open(gene_file, 'rt') as f:
            for line in islice(f, 1, None):
                components = line.strip().split('\t')
                gene_id = int(components[1])
                gene_name = components[2]
                if components[0] == self.HUMAN_SPECIES_ID and gene_name not in self.human_gene_dict:
                    self.human_gene_dict[gene_name] = gene_id

    def build_gene_mapper_index(self, gene_file=GENE_FILE):
        """
        builds dictionary to map all gene ids to human gene ids, if possible
        :param gene_file:
        :param index_file:
        :return:
        """
        logging.info('Computing index...')
        self.gene_to_human_id_dict.clear()
        self._build_human_gene_name_dict()
        with gzip.open(gene_file, 'rt') as f:
            for line in islice(f, 1, None):
                components = line.strip().split('\t')
                species_id, gene_id, gene_name = components[0:3]
                gene_id = int(gene_id)
                if species_id != self.HUMAN_SPECIES_ID and gene_name in self.human_gene_dict:
                    self.gene_to_human_id_dict[gene_id] = self.human_gene_dict[gene_name]

        logging.info('Writing index data to database...')
        session = Session.get()
        json_data = json.dumps(dict(human_gene_dict=self.human_gene_dict,
                                    gene_to_human_id_dict=self.gene_to_human_id_dict))
        EntityResolverData.overwrite_resolver_data(session, name=GeneMapper.NAME, json_data=json_data)

    def load_index(self):
        """
        load the index back from file
        :param index_file:
        :return:
        """
        session = Session.get()
        data = EntityResolverData.load_data_from_json(session, name=GeneMapper.NAME)
        if "human_gene_dict" in data and "gene_to_human_id_dict" in data:
            self.human_gene_dict = data["human_gene_dict"]
            self.gene_to_human_id_dict = data["gene_to_human_id_dict"]
        else:
            self.human_gene_dict = {}
            self.gene_to_human_id_dict = {}
        logging.info('Index for gene mapper load from database ({} keys)'.format(len(self.gene_to_human_id_dict)))

    def map_to_human_gene(self, gene_id):
        """
        Expects a gene id which is mapped to the corresponding humen gene
        Keyerror is thrown if no mapping exists
        :param gene_id: gene id which should be mapped to the human gene id
        :return: human gene id
        """
        return self.gene_to_human_id_dict[int(gene_id)]


def main():
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    gene_mapper = GeneMapper(load_index=False)
    gene_mapper.build_gene_mapper_index()


if __name__ == "__main__":
    main()
