# -*- coding: utf-8 -*-
"""
This module provides a generic specification for implementing the Data Access Object (DAO) design model.

The term 'data collection' refers to either a table in a relational database or a document in a NoSQL database.

This speciation will have to be implemented by each database system.
"""

import logging

ASC = ASCENDING = 1
"""Ascending sort order"""

DESC = DESCENDING = -1
"""Descending sort order"""


class PersistenceError(Exception):
    """
    Represents an error related to persistence operations.

    This class is designed to encapsulate errors that occur during persistence
    operations, such as saving or retrieving data. It provides means to pass
    a custom error message and an optional cause, offering more insight into
    what caused the error. This aids in debugging and understanding context
    in persistence-related failures.
    """

    def __init__(self, message='Persistence error', cause=None):
        """
        Represents an error related to persistence operations.

        This class extends the base Exception class to provide additional context
        for persistence-related errors, allowing an optional cause to be specified.

        :param message: The message describing the error.
        :param cause: The optional cause of the error.
        """
        super().__init__(message)
        self.cause = cause


class DuplicateKeyError(PersistenceError):
    """This exception is raised when trying to insert a record with a key that already exists in the data collection."""

    def __init__(self, data_collection, key, cause=None):
        """Represents an exception raised when a duplicate key is encountered in a data collection.

        :param data_collection: The data collection in which the duplicate key was encountered.
        :param key: The key that was already present in the data collection.
        """
        super().__init__(f'Duplicate key error : {key} already exist in data collection \'{data_collection}\'.', cause)
        self.data_collection = data_collection
        self.key = key


class ObjectNotFoundError(PersistenceError):
    """This exception is raised when trying to find a single record in a data set that does not exist."""

    def __init__(self, data_collection, key, cause=None):
        """
        Exception raised when an object is not found in the specified data set for a given key.

        :param data_collection: The data collection in which the object was not found.
        :param key: The key of the object that was not found.
        :param cause: The optional cause of the error.
        """
        super().__init__(f'Not object found with key {key} in data collection \'{data_collection}\'', cause)
        self.data_set = data_collection
        self.key = key


class DAO:
    """Generic definition of Data Access Object

    This class defines a common interface for all DAOs, so most methods will have to be overridden in subclasses,
    depending on the type of data collection used.

    """

    def __init__(self):
        """Instantiates a new DAO """
        self.logger = logging.getLogger(self.__class__.__name__)

    def find(self, query=None, skip=0, limit=0, sort=None, **kwargs):
        """Finds records matching the specified query.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving records matching the query from a data collection.
        If no matching record is found, the method returns an empty list.

        :param query: The filter used to query the data collection. If the query is None, all records are returned.
        :param skip: The number of records to omit (from the start of the result set) when returning the results.
        :param limit: The maximum number of records to return.
        :param sort: A list of (key, direction) pairs specifying the sort order for this list.
        :param kwargs: Implementation specific arguments.
        :return: The list of query matching records.
        """
        raise NotImplementedError()

    def find_all(self, skip=0, limit=0, sort=None, **kwargs):
        """Finds all the records.
        :param skip: The number of records to omit (from the start of the result set) when returning the results.
        :param limit: The maximum number of records to return.
        :param sort: A list of (key, direction) pairs specifying the sort order for this list.
        :param kwargs: Implementation specific arguments.
        :return: The list of all records.
        """
        return self.find(query=None, skip=skip, limit=limit, sort=sort, **kwargs)

    def find_one(self, query=None, **kwargs):
        """
        Finds a single record in the data collection that matches the given query.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving a single record from a data collection.
        If no matching record is found, the method may raise an ObjectNotFound error.

        :param query: The filter used to query the data collection. If the query is None, the first found record is returned.
        :param kwargs: Implementation specific arguments.
        :return: The record matching the query.
        :raises ObjectNotFoundError: If no record matches the given query.
        """
        raise NotImplementedError()

    def find_one_by_key(self, key, **kwargs):
        """Finds a record by its key.

        This method is intended to be overridden by subclasses to provide
        specific logic for retrieving a single identified record from a data collection.
        If no matching record is found, the method may raise an ObjectNotFound error.

        :param key: The key of the record
        :param kwargs: Implementation specific arguments.
        :return: The found record (if there is one).
        :raises ObjectNotFoundError: If no records match the specified key.
        """
        raise NotImplementedError()

    def count(self, query=None, **kwargs):
        """Counts the number of records

        This method is intended to be overridden by subclasses to provide
        specific logic for counting records matching the query from a data collection.
        If no matching record is found, the method returns an empty list.

        :param query: The filter used to query the data collection.
        :param kwargs: Implementation specific arguments.
        :return: The total number of records
        :rtype: int
        """
        raise NotImplementedError()

    def delete(self, query=None, **kwargs):
        """Deletes the record identified by the given key.

        This method is intended to be overridden by subclasses to provide
        specific logic for deleting a single record from a data collection.
        If no matching record is found, the method returns 0. Otherwise, it returns the number of deleted records.

        :param query: The filter used to query the records to delete from the data collection.
        :param kwargs: Implementation specific arguments.
        :return: The number of deleted records.
        :rtype: int
        """
        raise NotImplementedError()

    def delete_one_by_key(self, key, **kwargs):
        """Deletes the record identified by the given key.

        This method is intended to be overridden by subclasses to provide
        specific logic for deleting a single identified record from a data collection.
        It returns 1 if the record was deleted, 0 otherwise.

        :param key: The key of the record is to delete.
        :param kwargs: Implementation specific arguments.
        :return: The number of deleted records. (0 or 1)
        :rtype: int
        """
        raise NotImplementedError()

    def insert(self, data, **kwargs):
        """
        Inserts a new record into the data collection. 
        
        This method is intended to be overridden by subclasses to provide
        specific logic for inserting a single record into the data collection.
        It returns a dataset representing the inserted record.
        :param data: The data to insert.
        :param kwargs: Implementation specific arguments.
        :return: The inserted record.
        :raises DuplicateKeyError: If trying to insert a record with a key that already exists in the data collection.
        """
        raise NotImplementedError()

    def update(self, key, data, **kwargs):
        """
        Updates the record associated with the given key using provided data.

        This method is intended to be overridden in a subclass to provide
        specific logic for updating a single identified record into the data collection.
        It returns a dataset representing the updated record.

        :param key: The key of the record to update.
        :param data: The data to update.
        :param kwargs: Implementation specific arguments.
        :return: The updated record.
        :raises ObjectNotFoundError: If no record matches the given key.
        """
        raise NotImplementedError()

    def replace(self, key, data, **kwargs):
        """
        Replaces the record associated with the given key using provided data.

        This method is intended to be implemented by subclasses to provide the
        specific behavior for replacing a single identified record into the data collection. 
        It returns a dataset representing the replaced record.
        The key identifier has to be preserved during the replacement.

        :param key: The key of the record to replace.
        :param data: The data to replace.
        :param kwargs: Implementation specific arguments.
        :return: The replaced record.
        :raises ObjectNotFoundError: If no record matches the given key.
        """
        raise NotImplementedError()

    def upsert(self, key, data, **kwargs):
        """
        Tries to update an existing record identified by the given key or insert a new one if the key does not exist. 
        
        This method is intended to be implemented by subclasses to provide the specific behavior for updating a single
        identified record into the data collection, if it exists. Otherwise, it inserts a new record.
        It returns a dataset representing the updated record or the newly inserted record.

        :param key: The key of the record to update, if it exists.
        :param data: The data to update or insert.
        :param kwargs: Implementation specific arguments.
        :return: The updated or inserted record.
        """
        raise NotImplementedError()
