#!/usr/bin/env python
#
#   Copyright (c) 2016 In-Q-Tel, Inc, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
poseidonStorage interface for mongodb container
for persistent storage.

NAMES: current databases and collections (subject to change)

    db                      collection
    ---                     ---
    poseidon_records        network_graph
    poseidon_records        models

Created on 17 May 2016
@author: dgrossman, lanhamt
"""
import ConfigParser
import json
import sys
from os import environ
from subprocess import check_output
from urlparse import urlparse

import bson
import falcon
from falcon_cors import CORS
from pymongo import MongoClient


class poseidonStorage:
    """
    poseidonStorage class for managing mongodb database,
    brokers requests to database.

    NOTE: retrieves database host from config
    file in templates/config.template under the
    [database] section.
    """

    def __init__(self):
        self.modName = 'poseidonStorage'

        try:
            self.config = ConfigParser.ConfigParser()
            self.config.readfp(
                open('/poseidonWork/templates/config.template'))
            database_container_ip = self.config.get('database', 'ip')
        except:
            raise ValueError(
                'poseidonStorage: could not find database ip address.')
        self.client = MongoClient(host=database_container_ip)

        # create db named 'poseidon_records' (NOTE: db will not actually be
        # created until first doc write).
        # db stores reference object for the database
        self.db = self.client.poseidon_records


def get_allowed():
    rest_url = 'localhost:28000'
    if 'ALLOW_ORIGIN' in environ:
        allow_origin = environ['ALLOW_ORIGIN']
        host_port = allow_origin.split('//')[1]
        host = host_port.split(':')[0]
        port = str(int(host_port.split(':')[1]))
        rest_url = host + ':' + port
    else:
        allow_origin = ''
    return allow_origin, rest_url

allow_origin, rest_url = get_allowed()
cors = CORS(allow_all_origins=True)
public_cors = CORS(allow_all_origins=True)


class db_database_names(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    gets names of databases.
    """

    def on_get(self, req, resp):
        try:
            ret = self.client.database_names()
        except:
            ret = 'Error in connecting to mongo container'
        resp.body = json.dumps(ret)


class db_collection_names(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    get names of collections in given
    database.
    """

    def on_get(self, req, resp, database):
        ret = self.client[database].collection_names()
        # empty list returned for non-existent database
        if not ret:
            ret = 'Error on retrieving colleciton names.'
        resp.body = json.dumps(ret)


class db_collection_count(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    gets information for given collection.
    """

    def on_get(self, req, resp, database, collection):
        ret = self.client[database][collection].count()
        resp.body = json.dumps(ret)


class db_retrieve_doc(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    gets document in given database with given id.
    """

    def on_get(self, req, resp, database, collection, doc_id):
        ret = self.client[database][collection].find_one({'_id': doc_id})
        if not ret:
            ret = 'Error retrieving document with id: ' + doc_id + '.'
        resp.body = json.dumps(ret)


class db_collection_query(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    queries given database and collection,
    returns dict with the count of docs matching
    the query - if docs were found matching the query
    then includes a dict of ip->doc for each document.

    NOTE: supports bson encoding for well-formed
    queries (ie "{'node_ip': 'some ip'}")
    """

    def on_get(self, req, resp, database, collection, query_str):
        ret = {}
        try:
            query = bson.BSON.decode(query_str)
            cursor = self.client[database][collection].find(query)
            doc_dict = {}
            if cursor.count() == 0:
                ret['count'] = cursor.count()
                ret['docs'] = 'Valid query performed, no docs found.'
            else:
                for doc in cursor:
                    doc_dict[doc['node_ip']] = doc
                ret['docs'] = doc_dict
                ret['count'] = cursor.count()
            ret = json.dumps(ret)
        except:
            ret['count'] = -1
            ret['docs'] = 'Error on query.'
            ret = json.dumps(ret)
        resp.body = ret


class db_add_one_doc(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    adds a document to specified database and
    collection. returned response includes
    the id of the newly inserted object.

    NOTE: uses bson decoding for document
    to be inserted into database.
    """

    def on_get(self, req, resp, database, collection, doc_str):
        try:
            if not bson.is_valid(doc_str):
                doc_str = bson.BSON.encode(doc_str)
            ret = self.client[database][collection].insert_one(doc_str)
            ret = str(ret.inserted_id)
        except:
            ret = 'Error inserting document into database.'
        resp.body = json.dumps(ret)


class db_add_many_docs(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    adds a list of documents (encoded with
    bson) to specified database and collection.
    returned response includes the list of ids
    for the documents that have been inserted on
    success and error on failure.

    NOTE: uses bson decoding for documents to be
    inserted. Takes a string (doc_list) of concatenated
    bson-encoded map-objects (ie dicts).
    """

    def on_get(self, req, resp, database, collection, doc_list):
        try:
            doc_list = bson.decode_all(doc_list)
            ret = self.client[database][collection].insert_many(doc_list)
            for o_id in ret:
                o_id = str(o_id.inserted_id)
        except:
            ret = 'Error inserting documents into database.'
        resp.body = json.dumps(ret)


class db_update_one_doc(poseidonStorage):
    """
    rest layer subclass of poseidonStorage.
    udpates single document in database given
    a filter to find the document and an updated
    document.
    excepts on malformation but not on
    non-update - if there was no existing document
    found to update then 'updatedExisting' value of
    response will be False; if exception thrown then
    'success' value will be False.

    WARNING: replaces entire document with the
    updated_doc.
    """

    def on_get(self, req, resp, database, collection, filt, updated_doc):
        ret = {}
        try:
            ret = self.client[database][
                collection].updateOne(filt, updated_doc)
            ret['success'] = str(True)
        except:
            ret['success'] = str(False)
        resp.body = json.dumps(ret)


# create callable WSGI app instance for gunicorn
api = falcon.API(middleware=[cors.middleware])


# add local routes for db api
api.add_route('/v1/storage', db_database_names())
api.add_route(
    '/v1/storage/{database}',
    db_collection_names())
api.add_route(
    '/v1/storage/{database}/{collection}',
    db_collection_count())
api.add_route(
    '/v1/storage/doc/{database}/{collection}/{doc_id}',
    db_retrieve_doc())
api.add_route(
    '/v1/storage/query/{database}/{collection}/{query_str}',
    db_collection_query())
api.add_route(
    '/v1/storage/add_one_doc/{database}/{collection}/{doc_str}',
    db_add_one_doc())
api.add_route(
    '/v1/storage/add_many_docs/{database}/{collection}/{doc_list}',
    db_add_many_docs())
api.add_route(
    '/v1/storage/update_one_doc/{database}/{collection}/{filt}/{updated_doc}',
    db_update_one_doc())


def main():
    """
    Initialization to run in mongo container -
    pull desired database options from config.
    """
    pass


if __name__ == '__main__':
    main()
