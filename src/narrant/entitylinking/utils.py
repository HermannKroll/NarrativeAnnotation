from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.document.regex import DOCUMENT_ID


class DocumentError(Exception):
    pass


def get_document_id(fn):
    with open(fn) as f:
        line = f.readline()
    try:
        match = DOCUMENT_ID.match(line)
        if match:
            return int(match.group(1))
        else:
            doc = TaggedDocument(fn)
            return doc.id
    except AttributeError:
        raise DocumentError(f"No ID found for {fn}")
