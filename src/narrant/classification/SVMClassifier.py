import logging
import pickle
import random
from typing import Set, List

from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV

from kgextractiontoolbox.backend.database import Session
from kgextractiontoolbox.backend.models import Document
from kgextractiontoolbox.backend.retrieve import iterate_over_all_documents_in_collection
from kgextractiontoolbox.document.document import TaggedDocument
from kgextractiontoolbox.entitylinking.classifier import BaseClassifier


class SVMClassifier(BaseClassifier):
    TRAIN_RATIO = 0.8
    TEST_RATIO = 0.2

    def __init__(self, classification: str, model_path: str):
        super().__init__(classification)
        logging.info(f'Loading SVM (class = {classification}) files from {model_path}')
        self.model: svm.SVC = None
        self.vectorizer = None
        self.__load_model(model_path)

    def __load_model(self, model_path: str):
        logging.info(f'Loading SVM model from {model_path}')
        self.vectorizer = TfidfVectorizer()
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        logging.info('Model loaded')

    def classify_document(self, doc: TaggedDocument, consider_sections=False):
        """
        Applies the loaded SVM model to a list of documents
        :param doc: a document
        :param consider_sections: should the fulltext sections be considered
        :return: None
        """
        texts = [doc.get_text_content(sections=consider_sections)]
        text_vec = self.vectorizer.transform(texts)
        labels = self.model.predict(text_vec)
        if labels[0] == 1:
            doc.classification[self.classification] = "SVM"

    @staticmethod
    def get_negative_document_ids(positive_document_ids: Set[int], document_collection: str):
        """
        Gets a set of negative document ids (intersection of positive and negative documents will be empty)
        :param positive_document_ids: the set of positive document ids (to ensure an empty intersection)
        :param document_collection: the corresponding document collection
        :return:
        """
        session = Session.get()
        d_query = session.query(Document.id).filter(Document.collection == document_collection)
        negative_document_ids = set()
        for r in d_query:
            negative_document_ids.add(r[0])
        negative_document_ids = negative_document_ids - positive_document_ids
        return negative_document_ids

    @staticmethod
    def train_model(document_id_file: str, document_collection: str, model_path: str,
                    train_sample_size=100000, no_workers=-1):
        """
        Trains a SVM based on a set of document ids. Negative examples are randomly sampled from the database
        The SVM model learns to predict the document's class based on the title+abstract
        :param document_id_file: path to a file containing a list of document ids
        :param document_collection: the corresponding document collection in the database
        :param model_path: path to store the trained SVM model
        :param train_sample_size: how many documents should be sampled for training (Does not have an effect if the number of document ids is less than this parameter)
        :param no_workers: number of parallel works to train the SVM (-1 = no cores)
        :return: None
        """
        logging.info('Beginning SVM training...')

        logging.info(f'Loading document ids from {document_id_file}...')
        with open(document_id_file, 'rt') as f:
            pos_document_ids = set([int(line.strip()) for line in f])
        logging.info(f'{len(pos_document_ids)} positive document ids loaded')

        logging.info(f'Retrieving negative document ids from database...')
        neg_document_ids = SVMClassifier.get_negative_document_ids(positive_document_ids=pos_document_ids,
                                                                   document_collection=document_collection)
        logging.info(f'{len(neg_document_ids)} negative document ids retrieved')

        # Calculate the minimum sample size to be balanced
        max_sample_size = min([len(pos_document_ids), len(neg_document_ids), train_sample_size])
        logging.info(f'Working with sample size {max_sample_size}')

        pos_document_ids = random.sample(pos_document_ids, k=max_sample_size)
        neg_document_ids = random.sample(neg_document_ids, k=max_sample_size)
        logging.info(f'Computed {len(pos_document_ids)} positive / {len(neg_document_ids)} negative examples')

        logging.info('Retrieving texts from database....')
        session = Session.get()
        doc_ids = pos_document_ids + neg_document_ids
        x_data, y_data = [], []
        for doc in iterate_over_all_documents_in_collection(session=session, collection=document_collection,
                                                            document_ids=doc_ids):
            text = doc.get_text_content(sections=False)
            x_data.append(text)
            if doc.id in pos_document_ids:
                y_data.append(1)
            else:
                y_data.append(0)
        logging.info(f'Retrieved {len(x_data)} texts (and {len(y_data)} labels)')

        logging.info('Vectorizing texts (tfidf vectorizer)...')
        vectorizer = TfidfVectorizer()
        vectorizer.fit(x_data)
        x_data = vectorizer.transform(x_data)

        # Split into train and test
        x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=1 - SVMClassifier.TRAIN_RATIO)

        logging.info(f'Data split into {x_train.shape[0]} train / {x_test.shape[0]} test '
                     f'({SVMClassifier.TRAIN_RATIO}/{SVMClassifier.TEST_RATIO})')

        logging.info(f'Training SVM with Hyper-Parameter search (on train with cv = 10 and {no_workers} workers)...')
        param_grid = {'C': [0.1, 1, 100, 1000], 'kernel': ['rbf', 'poly', 'sigmoid'],
                      'degree': [1, 2, 3, 4, 5, 6]}
        grid = GridSearchCV(svm.SVC(), param_grid, cv=4, n_jobs=no_workers, verbose=10)
        grid.fit(x_train, y_train)

        logging.info(f'Found best parameters: {grid.best_params_}')
        logging.info(f'Model achieved {grid.score(x_test, y_test)} score on test')
        logging.info(f'Storing model to {model_path}')
        with open(model_path, 'wb') as f:
            pickle.dump(grid.best_estimator_, f)

        logging.info('Finished')
