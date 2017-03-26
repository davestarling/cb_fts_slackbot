"""Provides abstraction for couchbase objects."""

from couchbase.bucket import Bucket as CouchbaseBucket
from couchbase.exceptions import CouchbaseError, NotFoundError

import lib
from collections import OrderedDict


class CB(object):
    """Couchbase Abstraction Object."""

    def __init__(self, override_config=None):
        """
        Initialise the Couchbase object.

        If an override dictionary is passed then use that, otherwise use the
        defaults.

        :param override_config:
        """

        if override_config:
            self.cbbucket = override_config.get('bucket')
            self.cburl = override_config.get("url")
            self.cbpassword = override_config.get("password")
        else:
            self.cbbucket = lib.options.get("couchbase", "bucket")
            self.cburl = lib.options.get("couchbase", "url")
            self.cbpassword = lib.options.get("couchbase", "password")

        self.cb = None

    def create_connection(self):
        """Create a connection to Couchbase."""

        try:
            self.cb = CouchbaseBucket(connection_string=self.cburl,
                                      password=self.cbpassword)
        except:
            raise CB_Connection_Exception

    def save(self, key, value, cas=None, **kwargs):
        """
        Save a couchbase document.

        :param key:
        :param value:
        :param cas:
        :return:
        """
        if not self.cb:
            self.create_connection()

        if cas is not None:
            return self.cb.set(key, value, cas=cas)
        else:
            return self.cb.set(key, value)

    def save_multi(self, data, **kwargs):
        """
        Save multiple couchbase documents.

        :param data:
        :param kwargs:
        :return:
        """
        if not self.cb:
            self.create_connection()

        return self.cb.upsert_multi(data, **kwargs)

    def fetch(self, key):
        """
        Fetch a document by key.

        :param key:
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:
            result = self.cb.get(key)
            return result
        except NotFoundError:
            return False
        except CouchbaseError:
            return False

    def fetch_multi(self, keys):
        """
        Fetch multiple documents based on a list of keys.

        :param keys:
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:
            result = self.cb.get_multi(keys)
            return result
        except NotFoundError:
            return False
        except CouchbaseError:
            return False

    def delete(self, key):
        """
        Delete a specified document.

        :param key:
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:
            result = self.cb.delete(key)
            return result
        except CouchbaseError:
            return False

    def fetch_view(self, doc, view, **kwargs):
        """
        Fetch a view.

        :param doc:
        :param view:
        :param key:
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:

            result = self.cb.query(doc, view, **kwargs)

            return result
        except CouchbaseError:
            raise

    def execute_query(self, query, single_result=False, additional_creds=None):
        """
        Execute a N1QL query.

        :param query: N1QLQuery object
        :param single_result:
        :param additional_creds: List containing dictionaries of additional
                                 credentials for cross-bucket joins.
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:
            credentials = [{
                "user": "local:" + self.cbbucket,
                "pass": self.cbpassword
            }]

            if additional_creds:
                credentials += additional_creds

            query.set_option("creds", credentials)
            query.set_option("max_parallelism", "0")

            if single_result:
                result = self.cb.n1ql_query(query).get_single_result()
            else:
                result = self.cb.n1ql_query(query)

            return result
        except CouchbaseError:
            raise

    def mutate(self, key, *args):
        """
        Mutate a document using the Couchbase Subdocument API.

        :param key: The Couchbase Document ID to mutate
        :param args: One or more mutations to make against the document
        :return:
        """
        if not self.cb:
            self.create_connection()

        try:
            return self.cb.mutate_in(key, *args)
        except CouchbaseError:
            raise

    def fts_search(self, index_name, query, fields=None, highlight_fields=None,
                   highlight_style='html', limit=None, offset=None,
                   facets=None):
        """
        Search using FTS.

        :param index_name: The name of the FTS index against which the search
                           is run.
        :param query:
        :param fields:
        :param highlight_fields:
        :param highlight_style:
        :param limit:
        :param offset:
        :param facets:
        :return:
        """
        if self.cb is None:
            self.create_connection()

        try:

            params = {
                'highlight_style': highlight_style
            }

            if limit is not None:
                params['limit'] = limit

            if offset is not None:
                params['skip'] = offset

            if fields is not None:
                params['fields'] = fields

            if highlight_fields is not None:
                params['highlight_fields'] = highlight_fields

            if facets is not None:
                params['facets'] = facets

            return self.cb.search(index_name, query, **params)
        except CouchbaseError:
            raise

    def process_fts_result(self, result):
        """
        Run through an FTS result set.

        Fetches the documents and stores them in an ordered dictionary.

        :param result:
        :return: OrderedDict
        """
        if self.cb is None:
            self.create_connection()

        processed_results = {
            'total_hits': 0,
            'rows': OrderedDict()
        }

        ids_to_fetch = []

        for row in result:
            ids_to_fetch.append(row['id'])
            processed_results['rows'][row['id']] = row

        processed_results['total_hits'] = result.total_hits

        docs = self.fetch_multi(ids_to_fetch)

        if docs is False:
            return processed_results

        for key, doc in docs.items():
            processed_results['rows'][key]['doc'] = doc.value

        return processed_results


class CB_Connection_Exception(Exception):
    pass
