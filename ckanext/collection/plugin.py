import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from routes.mapper import SubMapper
import json

import logging
log = logging.getLogger(__name__)

class CollectionPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'collection')

    # IRoutes

    def before_map(self, map):
        with SubMapper(map, controller='ckanext.collection.controller:CollectionController') as m:
            m.connect('/collection', action='search_collection')

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
        log.debug(groups)
        if groups is not []:
            data_dict['collections'] = [group.get('display_name', '') for group in groups if group.get('type', "") == 'collection']

        data_dict['groups'] = [group for group in data_dict['groups'] if group not in data_dict['collections']]

        log.debug(data_dict)

        return data_dict