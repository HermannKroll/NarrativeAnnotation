from __future__ import annotations

import csv
import gzip
import json
import logging
from collections import defaultdict
from datetime import datetime
from itertools import islice

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Tag, EntityResolverData
from kgextractiontoolbox.entitylinking.tagging.vocabulary import Vocabulary
from narrant.config import GENE_FILE, MESH_DESCRIPTORS_FILE, TAXONOMY_FILE, \
    MESH_SUPPLEMENTARY_FILE, \
    DOSAGEFORM_TAGGER_VOCAB, VACCINE_TAGGER_VOCAB, \
    DRUG_TAGGER_VOCAB, ORGANISM_TAGGER_VOCAB, REGISTERED_VOCABULARIES
from narrant.entitylinking.enttypes import GENE, SPECIES, DOSAGE_FORM, LAB_METHOD, VACCINE
from narrant.mesh.data import MeSHDB
from narrant.mesh.supplementary import MeSHDBSupplementary


def get_gene_ids(session):
    logging.info('Querying gene ids in Tag table...')
    gene_ids_in_db = set()
    q = session.query(Tag.ent_id.distinct()).filter(Tag.ent_type == GENE)
    for r in session.execute(q):
        try:
            gene_ids_in_db.add(int(r[0]))
        except ValueError:
            continue
    logging.info('{} gene ids retrieved'.format(len(gene_ids_in_db)))
    return gene_ids_in_db


def get_species_ids(session):
    logging.info('Querying species ids in Tag table...')
    gene_ids_in_db = set()
    q = session.query(Tag.ent_id.distinct()).filter(Tag.ent_type == SPECIES)
    for r in session.execute(q):
        try:
            gene_ids_in_db.add(int(r[0]))
        except ValueError:
            continue
    logging.info('{} species ids retrieved'.format(len(gene_ids_in_db)))
    return gene_ids_in_db


class MeshResolver:
    """
    MeSHResolver translates MeSH descriptor ids into strings / headings
    """
    MESH_NAME = "MeSH"
    MESH_SUPPLEMENT_NAME = "MeSH supplementary"

    def __init__(self):
        self.desc2heading = {}
        self.supplement_desc2heading = {}

    def build_index(self, mesh_file=MESH_DESCRIPTORS_FILE, mesh_supp_file=MESH_SUPPLEMENTARY_FILE):
        logging.info('Reading mesh file: {}'.format(mesh_file))
        meshdb = MeSHDB()
        meshdb.load_xml(mesh_file)
        for desc in meshdb.get_all_descs():
            self.desc2heading[desc.unique_id] = desc.heading

        session = Session.get()
        json_data = json.dumps(self.desc2heading)
        logging.info(f'Writing MeSH index ({len(json_data)} keys) to DB (entity_resolver_data table)')
        EntityResolverData.overwrite_resolver_data(session, name=MeshResolver.MESH_NAME, json_data=json_data)

        logging.info('Reading mesh supplementary file: {}'.format(mesh_supp_file))
        mesh_supplementary: MeSHDBSupplementary = MeSHDBSupplementary()
        mesh_supplementary.load_xml(mesh_supp_file)
        for record in mesh_supplementary.get_all_records():
            self.supplement_desc2heading[record.unique_id] = record.name

        json_data = json.dumps(self.supplement_desc2heading)
        logging.info(f'Writing MeSH Supplement index ({len(json_data)} keys) to DB (entity_resolver_data table)')
        EntityResolverData.overwrite_resolver_data(session, name=MeshResolver.MESH_SUPPLEMENT_NAME, json_data=json_data)

    def load_index(self):
        start_time = datetime.now()
        session = Session.get()
        self.desc2heading = EntityResolverData.load_data_from_json(session, MeshResolver.MESH_NAME)
        logging.info('Mesh index ({} keys) load in {}s'.format(len(self.desc2heading), datetime.now() - start_time))
        start_time = datetime.now()

        self.supplement_desc2heading = EntityResolverData.load_data_from_json(session,
                                                                              MeshResolver.MESH_SUPPLEMENT_NAME)
        logging.info('Mesh Supplement index ({} keys) load in {}s'.format(len(self.supplement_desc2heading),
                                                                          datetime.now() - start_time))

    def descriptor_to_heading(self, descriptor_id):
        """
        returns a MeSH heading for a corresponding descriptor id
        throws key error if ID unknown
        :param descriptor_id: the MeSH Descriptor ID
        :return: corresponding MeSH heading
        """
        # first look in mesh db and then in supplementary
        try:
            return self.desc2heading[descriptor_id.replace('MESH:', '')]
        except KeyError:
            return self.supplement_desc2heading[descriptor_id.replace('MESH:', '')]


class GeneResolver:
    """
    GeneResolver translates NCBI Gene ids to a gene focus + gene name
    """
    NAME = "Gene"

    def __init__(self):
        self.geneid2name = {}
        self._genelocus2name = {}

    def get_reverse_index(self):
        term2entity = {}
        for e_id, (gene_focus, gene_name) in self.geneid2name.items():
            term2entity[gene_focus.strip().lower()] = gene_focus.strip().lower()
            term2entity[gene_name.strip().lower()] = gene_focus.strip().lower()
        return term2entity

    def build_index(self, gene_input=GENE_FILE, query_db_gene_ids=True):
        gene_ids_in_db = set()
        if query_db_gene_ids:
            gene_ids_in_db = get_gene_ids(Session.get())
        logging.info('Reading gene input file: {}'.format(gene_input))
        with gzip.open(gene_input, 'rt') as f:
            for line in islice(f, 1, None):
                components = line.strip().split('\t')
                gene_id = int(components[1])
                if query_db_gene_ids and gene_id not in gene_ids_in_db:
                    continue
                gene_symbol = components[2]
                description = components[8]
                self.geneid2name[gene_id] = (gene_symbol, description)

        logging.info('Writing index with {} keys to database'.format(len(self.geneid2name)))
        session = Session.get()
        json_data = json.dumps(self.geneid2name)
        EntityResolverData.overwrite_resolver_data(session, name=GeneResolver.NAME, json_data=json_data)

    def load_index(self):
        start_time = datetime.now()
        session = Session.get()
        self.geneid2name = EntityResolverData.load_data_from_json(session, GeneResolver.NAME)
        logging.info('Gene index ({} keys) load in {}s'.format(len(self.geneid2name), datetime.now() - start_time))

    def gene_id_to_name(self, gene_id):
        """
        Translates a NCBI Gene ID to a Gene description + focus
        If description and locus are available, Description//Focus is returned
        else either the gene descriptor or locus
        :param gene_id: NCBI Gene ID
        :return: Description//Symbol if available, else description / symbol
        """
        try:
            gene_id_int = int(gene_id)
            symbol, description = self.geneid2name[gene_id_int]
            if symbol and description:
                return '{}//{}'.format(description, symbol)
            elif not symbol:
                return '{}'.format(description)
            else:
                return '{}'.format(symbol)
        except ValueError:
            raise KeyError('Gene ids should be ints. {} is not an int'.format(gene_id))

    def gene_locus_to_description(self, locus):
        """
        Get the description for a gene locus
        If description is available description//locus will be returned else only the locus
        If called first, a index will be computed
        :param locus: the gene locus
        :return: if translation is available description//locus will be returned - else locus
        """
        locus = str(locus).lower()
        if not self._genelocus2name:
            logging.info('Computing genelocus2name index on the fly...')
            self._genelocus2name = {}
            for (l, description) in self.geneid2name.values():
                self._genelocus2name[str(l).lower()] = description
        if locus in self._genelocus2name:
            return '{}//{}'.format(self._genelocus2name[locus], locus)
        else:
            return '{}'.format(locus)

    def gene_id_to_symbol(self, gene_id):
        """
        Translates a NCBI Gene ID to a gene symbol like CYP3A4
        :param gene_id:
        :return:
        """
        gene_id_int = int(gene_id)
        symbol, _ = self.geneid2name[gene_id_int]
        return str(symbol).lower()


class SpeciesResolver:
    """
    SpeciesResolver translates a NCBI Species ID to the Species' common and scientific name
    """
    NAME = "Species"
    NAME_COMMON = 'genbank common name'
    NAME_COMMON_SHORTCUT = "c"
    NAME_SCIENTIFIC = "scientific name"
    NAME_SCIENTIFIC_SHORTCUT = "s"

    def __init__(self):
        self.speciesid2name = defaultdict(dict)
        trans_map = {p: '' for p in '[]()'}
        self.__translator = str.maketrans(trans_map)

    def get_reverse_index(self):
        s2n = dict()
        for sid, n_dict in self.speciesid2name.items():
            if self.NAME_COMMON_SHORTCUT in n_dict:
                s2n[n_dict[self.NAME_COMMON_SHORTCUT]] = sid
            if self.NAME_SCIENTIFIC_SHORTCUT in n_dict:
                s2n[n_dict[self.NAME_SCIENTIFIC_SHORTCUT]] = sid
        return s2n

    def build_index(self, species_input=TAXONOMY_FILE, query_db_species_ids=True):
        species_ids_in_db = set()
        if query_db_species_ids:
            species_ids_in_db = get_species_ids(Session.get())
        logging.info('Reading species input file: {}'.format(species_input))
        with gzip.open(species_input, 'rt') as f:
            for line in islice(f, 1, None):
                if self.NAME_COMMON in line or self.NAME_SCIENTIFIC in line:
                    components = line.split('\t')
                    species_id = components[0]
                    name = components[2]
                    # Remove brackets
                    name = name.translate(self.__translator).strip()

                    # skip species that are not in the Tag table
                    if query_db_species_ids and int(species_id) not in species_ids_in_db:
                        continue

                    if self.NAME_COMMON in line:
                        self.speciesid2name[species_id][self.NAME_COMMON_SHORTCUT] = name
                    else:
                        self.speciesid2name[species_id][self.NAME_SCIENTIFIC_SHORTCUT] = name

        logging.info('Writing index to database')
        session = Session.get()
        json_data = json.dumps(self.speciesid2name)
        EntityResolverData.overwrite_resolver_data(session, SpeciesResolver.NAME, json_data)

    def load_index(self):
        start_time = datetime.now()
        session = Session.get()
        self.speciesid2name = EntityResolverData.load_data_from_json(session, SpeciesResolver.NAME)
        logging.info('Species index ({} keys) load in {}s'.format(len(self.speciesid2name),
                                                                  datetime.now() - start_time))

    def species_id_to_name(self, species_id):
        """
        Translates a NCBI Species ID to the Species' common and scientific name
        :param species_id: NCBI Species ID
        :return: Common Species Name[//Scientific Species Name (if available)]
        """
        sp2name = self.speciesid2name[species_id]
        name = []
        if self.NAME_COMMON_SHORTCUT in sp2name:
            name.append(sp2name[self.NAME_COMMON_SHORTCUT])
        if self.NAME_SCIENTIFIC_SHORTCUT in sp2name:
            if name:
                name.append('//')
            name.append(sp2name[self.NAME_SCIENTIFIC_SHORTCUT])
        return ''.join(name)


class DosageFormResolver:
    """
    DosageFormResolver translates dosage form ids to their heading
    """

    def __init__(self, mesh_resolver):
        start_time = datetime.now()
        self.mesh = mesh_resolver
        self.dosageform_vocabulary = Vocabulary(DOSAGEFORM_TAGGER_VOCAB)
        self.dosageform_vocabulary.load_vocab(expand_terms=False)
        logging.info('DosageForm index ({} keys) load in {}s'.format(self.dosageform_vocabulary.size,
                                                                     datetime.now() - start_time))

    def dosage_form_to_name(self, dosage_form_id):
        """
        Translates a dosage form ID to it's name
        :param dosage_form_id: dosage form ID (either starting with MESH: or with FID)
        :return: Heading of the corresponding DosageForm
        """
        if dosage_form_id.startswith('MESH:'):
            return self.mesh.descriptor_to_heading(dosage_form_id)
        else:
            return self.dosageform_vocabulary.get_entity_heading(dosage_form_id, DOSAGE_FORM)


class ExcipientResolver:

    def excipient_id_to_name(self, excipient_id: str):
        # the id is already the name
        return excipient_id


class PlantFamilyResolver:

    def __init__(self):
        pass

    def plant_family_id_to_name(self, plant_family_to_name):
        return plant_family_to_name


class ChEMBLDatabaseResolver:

    def __init__(self):
        self.chemblid2name = {}

    def load_index(self, vocabularies: list[str] = [DRUG_TAGGER_VOCAB, ORGANISM_TAGGER_VOCAB]):
        self.chemblid2name.clear()
        start_time = datetime.now()

        for file in vocabularies:
            with open(file, 'rt') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in islice(reader, 1, None):
                    chembl_id = row[0].strip()
                    pref_name = row[2].lower().strip().capitalize()
                    if not chembl_id in self.chemblid2name.keys():
                        self.chemblid2name[chembl_id] = pref_name
        logging.info(f'{len(self.chemblid2name)} ChEMBL id mappings load in {(datetime.now() - start_time)}s')

    def chemblid_to_name(self, chembl_id: str) -> str:
        return self.chemblid2name[chembl_id]


class VaccineResolver:

    def __init__(self, mesh_resolver):
        start_time = datetime.now()
        self.mesh = mesh_resolver
        self.vaccine_vocab = Vocabulary(VACCINE_TAGGER_VOCAB)
        self.vaccine_vocab.load_vocab(expand_terms=False)
        logging.info('DosageForm index ({} keys) load in {}s'.format(self.vaccine_vocab.size,
                                                                     datetime.now() - start_time))

    def vaccine_to_heading(self, entity_id):
        """
        Returns the heading for a vaccine
        :param entity_id: vaccine id
        :return:
        """
        if entity_id.startswith('MESH:'):
            return self.mesh.descriptor_to_heading(entity_id)
        else:
            return self.vaccine_vocab.get_entity_heading(entity_id, VACCINE)


class EntityResolver:
    """
    EntityResolver translates an entity id and an entity type to it's corresponding name
    Automatically loads and initialise the resolvers for MeSH, DrugbankIDs, Gene, Species and DosageForms
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EntityResolver, cls).__new__(cls)
            cls.__instance.mesh = MeshResolver()
            cls.__instance.mesh.load_index()
            cls.__instance.gene = GeneResolver()
            cls.__instance.gene.load_index()
            cls.__instance.species = SpeciesResolver()
            cls.__instance.species.load_index()
            cls.__instance._entity_id_to_heading = None
            cls.__instance._load_registered_vocabularies()
        return cls.__instance

    def _load_registered_vocabularies(self, registered_vocabs=REGISTERED_VOCABULARIES):
        self._entity_id_to_heading = dict()
        for vocab_file in registered_vocabs:
            v = Vocabulary(vocab_file)
            v.load_vocab(expand_terms=False)
            for entry in v.vocabulary_entries:
                if entry.entity_id.startswith('CHEMBL'):
                    self._entity_id_to_heading[('CHEMBL', entry.entity_id)] = entry.heading
                else:
                    self._entity_id_to_heading[(entry.entity_type, entry.entity_id)] = entry.heading

    def get_name_for_var_ent_id(self, entity_id, entity_type, resolve_gene_by_id=True):
        """
        Translates an entity id and type to its name
        :param entity_id: the entity id
        :param entity_type: the entity type
        :param resolve_gene_by_id:
        :return: uses the corresponding resolver for the entity type
        """
        if entity_id.startswith('FIDXLM1') and entity_type == LAB_METHOD:
            return "Assay"
        if entity_id.startswith('MESH:'):
            return self.mesh.descriptor_to_heading(entity_id)
        if entity_type == GENE:
            if resolve_gene_by_id:
                return self.gene.gene_id_to_name(entity_id)
            else:
                return self.gene.gene_locus_to_description(entity_id)
        if entity_type == SPECIES:
            return self.species.species_id_to_name(entity_id)

        if entity_id.startswith('CHEMBL'):
            key = ('CHEMBL', entity_id)
        else:
            key = (entity_type, entity_id)
        try:
            return self._entity_id_to_heading[key].capitalize()
        except KeyError:
            pass

        # if entity one of [EXCIPIENT, PLANT_FAMILY_GENUS] the name is equal to the entity_id
        return entity_id.capitalize()


def main():
    """
    Automatically builds all indexes for the different entity resolvers
    Including: MeSHResolver, GeneResolver, SpeciesResolver and DosageFormResolver
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    mesh = MeshResolver()
    mesh.build_index()

    gene = GeneResolver()
    gene.build_index()

    species = SpeciesResolver()
    species.build_index()


if __name__ == "__main__":
    main()
