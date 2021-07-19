import re

from pathlib import Path
from typing import Union

from narrant.pubtator.document import TaggedDocument


class Classifyer:
    def __init__(self, classification, rule_path:Union[str, Path]=None, rules=None):
        self.rules = []
        self.classification = classification
        if rule_path:
            self.rules = Classifyer.read_ruleset(rule_path)
        elif rules:
            self.rules = rules
        else:
            raise ValueError("Either rules or rule_path must be given")

    def classify_document(self, doc:TaggedDocument):
        content = doc.get_text_content()
        for rule in self.rules:
            match = ""
            for term in rule:
                term_match = term.search(content)
                if not term_match:
                    break
                else:
                    match += f"{term.pattern}:{term_match.group(0)}{term_match.regs[0]};"
            else:
                doc.classification[self.classification] = match
                return doc

    @staticmethod
    def read_ruleset(filepath:Union[str, Path]):
        ruleset = []
        with open(filepath, "r") as f:
            for line in f:
                terms = [re.compile(term.strip().replace("*", "\\w+") + "\\b") for term in line.split("AND")]
                ruleset.append(terms)
        return ruleset