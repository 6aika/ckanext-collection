from ckan.lib.dictization.model_dictize import group_list_dictize
from ckan.model import Package
from flask import Blueprint
from flask.views import MethodView


import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import model
from ckan.lib.plugins import DefaultTranslation
import json
from ckanext.collection.logic import action
from ckan.logic import get_action
from ckan.plugins.toolkit import _, g, ObjectNotFound, NotAuthorized, abort, render, request
from ckan.lib import helpers as h, i18n as i18n

from collections import OrderedDict

NotFound = ObjectNotFound

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
    plugins.implements(plugins.IBlueprint)

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

    def before_dataset_index(self, data_dict):
        groups = json.loads(data_dict.get('data_dict', {})).get('groups',[])

        data_dict['collections'] = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']

        groups_to_remove = [group.get('name', '') for group in groups if group.get('type', "") == 'collection']
        data_dict['groups'] = [group for group in data_dict['groups'] if group not in groups_to_remove]

        translated_collection_names = {'fi': [], 'en': [], 'sv': []}
        if data_dict['collections']:
            for collection in data_dict['collections']:
                log.info(collection)
                full_collection = get_action('group_show')({}, {'id': collection, 'include_datasets': False,
                                                           'include_dataset_count': False, 'include_extras': True,
                                                           'include_users': False, 'include_groups': False,
                                                           'include_tags': False, 'include_followers': False})
                translated_collection_title = full_collection.get('title_translated', {})
                if translated_collection_title.get('fi'):
                    translated_collection_names['fi'].append(translated_collection_title['fi'])
                if translated_collection_title.get('en'):
                    translated_collection_names['en'].append(translated_collection_title['en'])
                if translated_collection_title.get('sv'):
                    translated_collection_names['sv'].append(translated_collection_title['sv'])
        data_dict['vocab_translated_collection_title_fi'] = translated_collection_names.get('fi')
        data_dict['vocab_translated_collection_title_en'] = translated_collection_names.get('en')
        data_dict['vocab_translated_collection_title_sv'] = translated_collection_names.get('sv')
        return data_dict


    # IActions

    def get_actions(self):
        return {
            'group_list_authz': action.group_list_authz,
            'api_collection_show': action.api_collection_show
        }

    # IFacets

    _LOCALE_ALIASES = {'en_GB': 'en'}
    def organization_facets(self, facets_dict, group_type, package_type):
        if group_type == 'collection':
            lang = i18n.get_lang()
            if lang in self._LOCALE_ALIASES:
                lang = self._LOCALE_ALIASES[lang]

            facets_dict = OrderedDict()
            facets_dict.update({'res_format': _('Formats')})
            facets_dict.update({'vocab_geographical_coverage': _('Geographical Coverage')})
            facets_dict.update({'vocab_translated_group_title_' + lang: _('Groups')})
            facets_dict.update({'organization': _('Organizations')})
            facets_dict.update({'vocab_translated_collection_title_' + lang: _('Collections')})

        return facets_dict

    # IBlueprint
    def get_blueprint(self):
        collection_blueprint = Blueprint('collections', self.__module__, url_prefix=u'/dataset', url_defaults={u'package_type': u'dataset'})
        collection_blueprint.template_folder = 'templates'

        collection_blueprint.add_url_rule('/collections/<id>', 'dataset_collections', view_func=GroupView.as_view('collections'))

        return collection_blueprint


class GroupView(MethodView):
    def _prepare(self, id):
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'for_view': True,
            u'auth_user_obj': g.userobj,
            u'use_cache': False
        }

        try:
            pkg_dict = get_action(u'package_show')(context, {u'id': id})
        except (NotFound, NotAuthorized):
            return abort(404, _(u'Dataset not found'))
        return context, pkg_dict

    def post(self, package_type, id):
        context, pkg_dict = self._prepare(id)
        new_collection = request.form.get(u'collection_added')
        if new_collection:
            data_dict = {
                u"id": new_collection,
                u"object": id,
                u"object_type": u'package',
                u"capacity": u'public'
            }
            try:
                get_action(u'member_create')(context, data_dict)
            except NotFound:
                return abort(404, _(u'Collection not found'))

        removed_collection = None
        for param in request.form:
            if param.startswith(u'collection_remove'):
                removed_collection = param.split(u'.')[-1]
                break
        if removed_collection:
            data_dict = {
                u"id": removed_collection,
                u"object": id,
                u"object_type": u'package'
            }

            try:
                get_action(u'member_delete')(context, data_dict)
            except NotFound:
                return abort(404, _(u'Group not found'))
        return h.redirect_to('collections.dataset_collections', id=id)

    def get(self, package_type, id):
        context, pkg_dict = self._prepare(id)
        dataset_type = pkg_dict[u'type'] or package_type
        context[u'is_member'] = True

        pkg_obj = Package.get(pkg_dict['id'])
        collection_list = group_list_dictize(pkg_obj.get_groups('collection', None), context)
        data_dict = {'id': id, 'type': 'collection', 'all_fields': True, 'include_extras': True}

        # Every collection will get listed here instead of using group_list_authz as implemented in CKAN core groups,
        # since group_list_authz does not support group type
        collections = get_action('group_list')(context, data_dict)

        users_collections = get_action(u'group_list_authz')(context, data_dict)

        pkg_group_ids = set(
            group[u'id'] for group in collection_list
        )

        user_collection_ids = set(group[u'id'] for group in users_collections)
        cols = [collection for collection in collections if collection['id'] in user_collection_ids]

        collection_list = [collection for collection in collections if collection['id'] in pkg_group_ids]

        collection_dropdown = [[group[u'id'], group]
                          for group in cols
                          if group[u'id'] not in pkg_group_ids]

        for collection in collection_list:
            collection[u'user_member'] = (collection[u'id'] in user_collection_ids)

        return render(
            u'package/collection_list.html', {
                u'dataset_type': dataset_type,
                u'pkg_dict': pkg_dict,
                u'collection_dropdown': collection_dropdown,
                u'collection_list': collection_list
            }
        )