import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from routes.mapper import SubMapper
from ckan.lib.plugins import DefaultTranslation
import json
from ckanext.collection.logic import action, auth

import logging
log = logging.getLogger(__name__)

class CollectionPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    if toolkit.check_ckan_version(min_version='2.5.0'):
        plugins.implements(plugins.ITranslation, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'collection')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')

        schema.update({
            'ckanext.collection.api_collection_name_or_id': [ignore_missing, unicode],
        })

        return schema

    # IRoutes

    def before_map(self, map):
        with SubMapper(map, controller='ckanext.collection.controller:CollectionController') as m:
            m.connect('/collection', action='index')

            m.connect('/collection/new', action='new')

            m.connect('/collection/:id', action='read')

            m.connect('/collection/edit/:id', action='edit')

            m.connect('/collection/delete/:id', action='delete')

            m.connect('/collection/about/:id', action='about')

            m.connect('dataset_collection_list', '/dataset/collections/{id}',
                      action='dataset_collection_list', ckan_icon='picture')

        map.redirect('/collections', '/collection')

        return map

    def before_index(self, data_dict):
        groups = json.loads(data_dict.get('data_dict', {})).get('groups',[])

        data_dict['collections'] = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']

        groups_to_remove = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']
        data_dict['groups'] = [group for group in data_dict['groups'] if group not in groups_to_remove]

        return data_dict

    # IActions

    def get_actions(self):
        return {
            'group_list_authz': auth.group_list_authz,
            'api_collection_show': action.api_collection_show
        }