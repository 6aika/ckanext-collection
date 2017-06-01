import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from pylons import config

get_action = logic.get_action

@toolkit.side_effect_free
def api_collection_show(context, data_dict):
    data_dict = {
        'include_extras': False,
        'include_datasets': False, # Set to False to prevent group_dictize from calling package_search
        'include_dataset_count': False, # Set to False to prevent group_dictize from calling package_search
        'include_users': False,
        'include_groups': False,
        'include_followers': False,
        'include_tags': False,
        'id': config.get('ckanext.collection.api_collection_name_or_id')
    }
    collection = get_action('group_show')(context, data_dict)

    # group_dictize (called in group_show) does not support group types so a separate package_search is needed
    # to include the package count
    if collection:
        search_dict = {
            'fq': 'collections:' + collection['name'],
            'include_private': False,
        }
        collection_packages = get_action('package_search')(context, search_dict)
        collection['package_count'] = collection_packages['count']

    return collection
