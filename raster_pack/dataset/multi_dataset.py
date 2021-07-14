# External Imports
import uuid
from typing import Optional, Dict, List
import logging
import sqlite3

# Internal Imports
from raster_pack.dataset.dataset import Dataset

# Set up Logger
logger = logging.getLogger("raster_pack.dataset.multi_dataset")


class MultiDataset:
    datasets: Dict[str, Dataset]
    _db_con: sqlite3.Connection
    _db_cur: sqlite3.Cursor

    def __init__(self, datasets: Optional[List[Dataset]] = None):
        # Create dict for references to Dataset objects
        self.datasets = {}

        # Initialize a new in-memory sqlite database
        self._db_con = sqlite3.connect(database=":memory:")

        # Access database cursor
        self._db_cur = self._db_con.cursor()

        # Create table for dataset information
        self._db_cur.execute('''
        CREATE TABLE datasets
        (hash_value text, datetime text, subdataset_of text);
        ''')

        # Commit creation of table
        self._db_con.commit()

        # Add all the datasets if they exist
        if datasets is not None:
            self.insert_many(datasets)

    def insert_many(self, datasets: List[Dataset], subdataset_of: Optional[str] = None) -> None:
        """Insert all Dataset objects in a list

        Insert multiple Dataset objects contained within a list into the MultiDataset.

        :param datasets: The list of Dataset objects to insert
        :param subdataset_of: (Optional) Hash string of the associated parent dataset
        """

        # Verify correct conditions
        assert datasets is not None
        assert type(datasets) is list

        # Add each Dataset in the list of Dataset objects
        for dataset in datasets:
            # Create a UUID to refer to this specific dataset in the dict and database
            # Note: This is really not an efficient or well-designed way to do things
            hash_identifier = str(uuid.uuid4())

            # Add dataset to the internal list of datasets
            # Note: We add even the subdatasets to the dictionary so they can be referenced easily using an identifier
            self.datasets[hash_identifier] = dataset

            # Add entry for the dataset to the database table
            self._db_cur.execute(
                '''INSERT INTO datasets VALUES (?, ?, ?);''',
                (hash_identifier, dataset.meta["date"], "" if subdataset_of is None else subdataset_of)
            )

            # Commit database insertions
            self._db_con.commit()

            # Insert all subdatasets with a recursive call
            if dataset.subdatasets is not None and len(dataset.subdatasets) > 0:
                self.insert_many(datasets=dataset.subdatasets, subdataset_of=hash_identifier)

    def insert(self, dataset: Dataset) -> None:
        """Insert a Dataset

        Insert a single dataset into the MultiDataset

        :param dataset: The Dataset object to insert
        """
        self.insert_many(datasets=[dataset])

    def execute_in_db(self, command: str) -> sqlite3.Cursor:
        """Execute SQL in the in-memory SQLite backing database

        :param command: The SQL to run
        :return: A sqlite3 Cursor object upon which additional sqlite3 functions can be called
        """
        return self._db_cur.execute(command)
