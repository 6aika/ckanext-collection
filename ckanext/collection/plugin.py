import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import json
from ckanext.collection.logic import action
from ckan.logic import get_action
from ckan.plugins.toolkit import _

from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

unicode_safe = toolkit.get_validator('unicode_safe')


class CollectionPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    if toolkit.check_ckan_version(min_version='2.5.0'):
        plugins.implements(plugins.ITranslation, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IFacets, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'collection')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')

        schema.update({
            'ckanext.collection.api_collection_name_or_id': [ignore_missing, unicode_safe],
        })

        return schema

    def before_index(self, data_dict):
        groups = json.loads(data_dict.get('data_dict', {})).get('groups',[])

        data_dict['collections'] = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']

        groups_to_remove = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']
        data_dict['groups'] = [group for group in data_dict['groups'] if group not in groups_to_remove]

        return data_dict

    def after_search(self, search_results, search_params):
        if search_results['search_facets'].get('collections'):
            context = {'for_view': True, 'with_private': False}
            data_dict = {
                'all_fields': True,
                'include_extras': True,
                'type': 'collection'
            }
            collections_with_extras =get_action('group_list')(context, data_dict)

            for i, facet in enumerate(search_results['search_facets']['collections'].get('items', [])):
                for collection in collections_with_extras:
                    if facet['name'] == collection['name']:
                        search_results['search_facets']['collections']['items'][i]['title_translated'] = collection.get('title_translated')
                        if not collection.get('title_translated').get('en'):
                            search_results['search_facets']['collections']['items'][i]['title_translated']['en'] = collection.get('title')
                        if not collection.get('title_translated').get('sv'):
                            search_results['search_facets']['collections']['items'][i]['title_translated']['sv'] = collection.get('title')

        return search_results

    # IActions

    def get_actions(self):
        return {
            'group_list_authz': action.group_list_authz,
            'api_collection_show': action.api_collection_show
        }

    # IFacets

    def group_facets(self, facets_dict, group_type, package_type):

        if group_type == 'collection':
            facets_dict = OrderedDict()
            facets_dict.update({'res_format': _('Formats')})
            facets_dict.update({'vocab_geographical_coverage': _('Geographical Coverage')})
            facets_dict.update({'groups': _('Groups')})
            facets_dict.update({'organization': _('Organizations')})
            facets_dict.update({'collections': _('Collections')})

        return facets_dict