from nose import tools as nosetools

import logging
log = logging.getLogger(__name__)

import ckan.tests.helpers as helpers

submit_and_follow = helpers.submit_and_follow


class TestCollectionIndex(helpers.FunctionalTestBase):

    def test_collections_redirects_to_collection(self):
        '''/collections redirects to /collection.'''
        app = self._get_test_app()
        response = app.get('/collections', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/collection')