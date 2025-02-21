"""
XML Documentation: https://www.nlm.nih.gov/mesh/xml_data_elements.html
"""
import itertools
from datetime import datetime
from typing import List

from lxml import etree

from narrant.mesh.utils import get_text, get_attr, get_datetime, get_element_text, get_list

MESH_QUERY_DESCRIPTOR_RECORD = "/DescriptorRecordSet/DescriptorRecord"
MESH_QUERY_DESCRIPTOR_BY_ID = "/DescriptorRecordSet/DescriptorRecord/DescriptorUI[text()='{}']/parent::*"
MESH_QUERY_DESCRIPTOR_BY_TREE_NUMBER = "/DescriptorRecordSet/DescriptorRecord/TreeNumberList" \
                                       "/TreeNumber[text()='{}']/parent::*/parent::*"
MESH_QUERY_DESCRIPTOR_IDS_BY_TREE_NUMBER = "/DescriptorRecordSet/DescriptorRecord/TreeNumberList" \
                                           "/TreeNumber[starts-with(text(),'{}')]/parent::*/parent::*/DescriptorUI"
MESH_QUERY_DESCRIPTOR_BY_HEADING_CONTAINS = "/DescriptorRecordSet/DescriptorRecord/DescriptorName" \
                                            "/String[contains(text(),'{}')]/parent::*/parent::*"
MESH_QUERY_DESCRIPTOR_BY_HEADING_EXACT = "/DescriptorRecordSet/DescriptorRecord/DescriptorName" \
                                         "/String[text()='{}']/parent::*/parent::*"
MESH_QUERY_DESCRIPTOR_BY_TERM = "/DescriptorRecordSet/DescriptorRecord/ConceptList/Concept/TermList/Term" \
                                "/String[text()='{}']/parent::*/parent::*/parent::*/parent::*/parent::*"


class BaseNode:
    _attrs = dict()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__class__._attrs.keys():
                setattr(self, key, value)

    @classmethod
    def from_element(cls, record, *args):
        kwargs = dict()
        for key, (func, *func_args) in cls._attrs.items():
            kwargs[key] = func(record, *func_args)
        return cls(**kwargs)

    def print(self, print_unset=False):
        for key in self._attrs.keys():
            if getattr(self, key, None) or print_unset:
                print(f"{key}={getattr(self, key)}")

    @property
    def attrs(self):
        return tuple(self._attrs.keys())


class Term(BaseNode):
    _attrs = dict(
        abbreviation=(get_text, "Abbreviation"),
        concept_preferred_term_yn=(get_attr, "ConceptPreferredTermYN"),
        date_created=(get_datetime, "DateCreated"),
        entry_version=(get_text, "EntryVersion"),
        is_permuted_term_yn=(get_attr, "IsPermutedTermYN"),
        lexical_tag=(get_attr, "LexicalTag"),
        record_preferred_term_yn=(get_attr, "RecordPreferredTermYN"),
        sort_version=(get_text, "SortVersion"),
        _string=(get_text, "String", True),
        term_note=(get_text, "TermNote"),
        term_ui=(get_text, "TermUI", True),
        thesaurus_id_list=(get_list, "ThesaurusIDList", get_element_text),
    )

    @property
    def id(self):
        return getattr(self, "term_ui")

    @property
    def string(self):
        return getattr(self, "_string")

    def __str__(self):
        return "<Term {}>".format(self.string)

    def __repr__(self):
        return "<Term {} at {}>".format(self.string, self.id)


# TODO: Add reference to concept
class ConceptRelation(BaseNode):
    _attrs = dict(
        concept1ui=(get_text, "Concept1UI"),
        concept2ui=(get_text, "Concept2UI"),
        relation_name=(get_attr, "RelationName"),
    )


class Concept(BaseNode):
    _attrs = dict(
        cas_type_1_name=(get_text, "CASN1Name"),
        concept_relation_list=(get_list, "ConceptRelationList", ConceptRelation.from_element),
        _concept_ui=(get_text, "ConceptUI", True),
        _name=(get_text, "ConceptName/String", True),
        preferred_concept_yn=(get_attr, "PreferredConceptYN"),
        registry_number=(get_text, "RegistryNumber"),
        related_registry_number_list=(get_list, "RelatedRegistryNumberList", get_element_text),
        _scope_note=(get_text, "ScopeNote"),
        term_list=(get_list, "TermList", Term.from_element, True),
        translators_english_scope_note=(get_text, "TranslatorsEnglishScopeNote"),
        translators_scope_note=(get_text, "TranslatorsScopeNote"),
    )

    @property
    def name(self):
        return getattr(self, "_name")

    @property
    def concept_ui(self):
        return getattr(self, "_concept_ui")

    @property
    def scope_note(self):
        return getattr(self, "_scope_note")

    def __str__(self):
        return "<Concept {} ({})>".format(self.name, self.concept_ui)

    def __repr__(self):
        return "<Concept {} ({})>".format(self.name, self.concept_ui)


# TODO: Add reference to descriptor
class PharmacologicalAction(BaseNode):
    pass


# TODO: Add reference to descriptor
class SeeRelatedDescriptor(BaseNode):
    pass


class AllowableQualifier(BaseNode):
    _attrs = dict(
        _qualifier_ui=(get_text, "QualifierReferredTo/QualifierUI"),
        _qualifier_name=(get_text, "QualifierReferredTo/QualifierName/String")
    )

    @property
    def name(self):
        return getattr(self, "_qualifier_name")

    @property
    def ui(self):
        return getattr(self, "_qualifier_ui")


# noinspection PyUnresolvedReferences
class Descriptor(BaseNode):
    _attrs = dict(
        annotation=(get_text, "Annotation"),
        concept_list=(get_list, "ConceptList", Concept.from_element, True),
        consider_also=(get_text, "ConsiderAlso"),
        date_created=(get_datetime, "DateCreated"),
        date_revised=(get_datetime, "DateRevised"),
        date_established=(get_datetime, "DateEstablished", True),
        descriptor_class=(get_attr, "DescriptorClass"),
        _name=(get_text, "DescriptorName/String", True),
        history_note=(get_text, "HistoryNote"),
        nlm_classification_number=(get_text, "NLMClassificationNumber"),
        mesh_note=(get_text, "PublicMeSHNote"),
        online_note=(get_text, "OnlineNote"),
        pharmacological_action_list=(get_list, "PharmacologicalActionList", PharmacologicalAction.from_element),
        previous_indexing_list=(get_list, "PreviousIndexingList", get_element_text),
        scr_class=(get_attr, "SCRClass"),
        see_related_list=(get_list, "SeeRelatedList", SeeRelatedDescriptor.from_element),
        tree_number_list=(get_list, "TreeNumberList", get_element_text, True),
        _unique_id=(get_text, "DescriptorUI", True),
        allowable_qualifiers_list=(get_list, "AllowableQualifiersList", AllowableQualifier.from_element)
    )

    @property
    def heading(self) -> str:
        return getattr(self, "_name")

    @property
    def name(self) -> str:
        return getattr(self, "_name")

    @property
    def unique_id(self) -> str:
        return getattr(self, "_unique_id")

    @property
    def tree_numbers(self) -> List[str]:
        return getattr(self, "tree_number_list")

    @property
    def note(self) -> str:
        return getattr(self, "mesh_note")

    @property
    def allowable_qualifiers(self) -> List[AllowableQualifier]:
        return getattr(self, "allowable_qualifiers_list")

    @property
    def parents(self):
        if not hasattr(self, "_parents"):
            parent_tns = [".".join(tn.split(".")[:-1]) for tn in self.tree_numbers if "." in tn]
            parents = [MeSHDB().desc_by_tree_number(tn) for tn in parent_tns]
            setattr(self, "_parents", parents)
        return getattr(self, "_parents")

    @property
    def lineages(self):
        """
        :return: List of lists of Descriptors.
        """
        if not hasattr(self, "_lineages"):
            parent_lineages = [lineage for p in self.parents for lineage in p.lineages]
            if parent_lineages:
                lineages = [lineage + [self] for lineage in parent_lineages]
            else:
                lineages = [[self]]
            setattr(self, "_lineages", lineages)
        return getattr(self, "_lineages")

    def get_common_lineage(self, other):
        common = [[x for x, y in zip(l1, l2) if x == y] for l1 in self.lineages for l2 in other.lineages]
        return [x for x in common if x]

    @property
    def terms(self) -> List[Term]:
        if not hasattr(self, "_terms"):
            terms = list(itertools.chain.from_iterable(c.term_list for c in self.concept_list))
            setattr(self, "_terms", terms)
        return getattr(self, "_terms")

    def __str__(self):
        return "<Descriptor {}>".format(getattr(self, "heading"))

    def __repr__(self):
        return "<Descriptor {} at {}>".format(getattr(self, "heading"), id(self))

    def __lt__(self, other):
        return self.unique_id < other.unique_id


# noinspection PyTypeChecker,PyUnresolvedReferences
class MeSHDB:
    """
    Class is a Singleton for the MeSH database. You can load a descriptor file and query descriptors with the functions

    - desc_by_id
    - desc_by_tree_number
    - descs_by_name
    - descs_by_term
    """
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.tree = None
            cls.__instance._desc_by_id = dict()
            cls.__instance._desc_by_tree_number = dict()
            cls.__instance._desc_by_name = dict()
        return cls.__instance

    def get_index(self):
        return dict(
            _desc_by_id=self._desc_by_id,
            _desc_by_tree_number=self._desc_by_tree_number,
            _desc_by_name=self._desc_by_name,
        )

    def set_index(self, index):
        for key, value in index.items():
            setattr(self, key, value)

    def load_xml(self, filename, verbose=False, force_load=False):
        if not self._desc_by_id or force_load:
            start = datetime.now()
            self.tree = etree.parse(filename)
            end = datetime.now()
            if verbose:
                print("XML loaded in {}".format(end - start))

    def get_all_descs(self) -> List[Descriptor]:
        descs = []
        records = self.tree.xpath(MESH_QUERY_DESCRIPTOR_RECORD)
        for idx, record in enumerate(records):
            desc = Descriptor.from_element(record)
            descs.append(desc)
        return descs

    def add_desc(self, desc_obj):
        """
        Adds an descriptor to the indexes.

        .. note::

           The try-except was introduced because some descriptors (e.g., Female) don't have a tre number.

        :param desc_obj: Descriptor object to add
        """
        self._desc_by_id[desc_obj.unique_id] = desc_obj
        for tn in desc_obj.tree_numbers:
            self._desc_by_tree_number[tn] = desc_obj
        self._desc_by_name[desc_obj.heading] = desc_obj

    def desc_by_id(self, unique_id):
        if unique_id not in self._desc_by_id:
            query = MESH_QUERY_DESCRIPTOR_BY_ID.format(unique_id)
            desc_rec = self.tree.xpath(query)
            if desc_rec:
                desc = Descriptor.from_element(desc_rec[0])
                self.add_desc(desc)
            else:
                raise ValueError("Descriptor {} not found.".format(unique_id))
        return self._desc_by_id[unique_id]

    def descs_under_tree_number(self, tree_number):
        query = MESH_QUERY_DESCRIPTOR_IDS_BY_TREE_NUMBER.format(tree_number + ".")
        records = self.tree.xpath(query)
        ids = [record.text.strip() for record in records]
        desc_list = [self.desc_by_id(uid) for uid in ids]
        return sorted(desc_list)

    def desc_by_tree_number(self, tree_number):
        if tree_number not in self._desc_by_tree_number:
            query = MESH_QUERY_DESCRIPTOR_BY_TREE_NUMBER.format(tree_number)
            desc_rec = self.tree.xpath(query)
            if desc_rec:
                desc = Descriptor.from_element(desc_rec[0])
                self.add_desc(desc)
            else:
                raise ValueError("Descriptor {} not found.".format(tree_number))
        return self._desc_by_tree_number[tree_number]

    def descs_by_term(self, term):
        query = MESH_QUERY_DESCRIPTOR_BY_TERM.format(term)
        records = self.tree.xpath(query)
        desc_list = [Descriptor.from_element(record) for record in records]
        # Add to cache
        for desc in desc_list:
            if desc.unique_id not in self._desc_by_id:
                self.add_desc(desc)
        return desc_list

    def descs_by_name(self, name, match_exact=True, search_terms=True):
        if match_exact and name in self._desc_by_name:
            return [self._desc_by_name[name]]
        if match_exact:
            query = MESH_QUERY_DESCRIPTOR_BY_HEADING_EXACT.format(name)
        else:
            query = MESH_QUERY_DESCRIPTOR_BY_HEADING_CONTAINS.format(name)
        records = self.tree.xpath(query)
        desc_list = [Descriptor.from_element(record) for record in records]
        # Add to cache
        for desc in desc_list:
            if desc.unique_id not in self._desc_by_id:
                self.add_desc(desc)
        # Search by terms
        if not desc_list and search_terms:
            desc_list = self.descs_by_term(name)
        # Return
        return desc_list

    def get_descs_starting_with(self, char):
        result = []
        for x in self.get_all_descs():
            if not x.tree_numbers:
                continue

            tree_number = x.tree_numbers[0]
            for t in x.tree_numbers[1:]:
                tree_number += ';{}'.format(t)
            number_list = tree_number.split(';')
            for i in number_list:
                if i.startswith('C') and i.count('.') == 0:
                    result.append(i)
        result.sort()
        return result

    def extract_disease_json(self):
        diseases = self.get_descs_starting_with('C')
        diseases_string = ''
        for x in diseases:
            if x != diseases[0]:
                diseases_string = diseases_string[:-1]
                diseases_string += ', ' + self.build_string(self.desc_by_tree_number(x))[1:]
            else:
                diseases_string += self.build_string(self.desc_by_tree_number(x))
        return diseases_string

    def build_string(self, node):
        par_tree = node.tree_numbers[0]
        for t in node.tree_numbers[1:]:
            par_tree += '; {}'.format(t)
        par_tree_list = par_tree.split("; ")
        par_tree_str = par_tree_list[0]
        first_dots = par_tree_str.count('.')
        if len(self.descs_under_tree_number(par_tree_str)) == 0:
            result_string = '[{"name": "' + self.desc_by_tree_number(
                par_tree_str).heading + '", "children": [{"name": "(MESH:' + self.desc_by_tree_number(
                par_tree_str).unique_id + ')"}]}, '
        else:
            result_string = '[{"name": "' + self.desc_by_tree_number(
                par_tree_str).heading + ' (MESH:' + self.desc_by_tree_number(
                par_tree_str).unique_id + ')", "children": '
        child_list = self.descs_under_tree_number(par_tree_str)
        result = []
        for e in child_list:
            num = e.tree_numbers[0]
            for t in e.tree_numbers[1:]:
                num += ';{}'.format(t)
            temp_list = num.split(";")
            for x in temp_list:
                if x not in result and x.startswith(par_tree_str):
                    result.append(x)
        result.sort()
        last_leaf_branch = 1
        check_dots = par_tree_str.count('.')
        for element in result:
            if len(self.descs_under_tree_number(element)) == 0:  # and element.count('.') >= check_dots:
                if element.count('.') < check_dots:
                    result_string = result_string[:len(result_string) - 2]
                    for i in range(0, check_dots - element.count('.')):
                        result_string += ']}'
                    result_string += ', '
                if last_leaf_branch == 1:
                    result_string += '['
                result_string += '{"name": "' + self.desc_by_tree_number(
                    element).heading + '", "children": [{"name": "(MESH:' + self.desc_by_tree_number(
                    element).unique_id + ')"}]}, '
                last_leaf_branch = 0
                check_dots = element.count('.')
            else:
                if last_leaf_branch == 0:
                    result_string = result_string[:len(result_string) - 2]
                    if element.count('.') < check_dots:
                        for i in range(0, check_dots - element.count('.')):
                            result_string += ']}'
                    else:
                        for i in range(0, element.count('.') - check_dots):
                            result_string += ']}'
                    result_string += ', '
                    result_string += '{"name": "' + self.desc_by_tree_number(
                        element).heading + ' (MESH:' + self.desc_by_tree_number(element).unique_id + ')", "children": '
                else:
                    result_string += '[{"name": "' + self.desc_by_tree_number(
                        element).heading + ' (MESH:' + self.desc_by_tree_number(element).unique_id + ')", "children": '
                last_leaf_branch = 1
                check_dots = element.count('.')
        result_string = result_string[:len(result_string) - 2]
        result_string += ']'
        for i in range(0, check_dots - first_dots):
            result_string += '}]'
        return result_string
