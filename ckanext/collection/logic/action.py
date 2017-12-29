import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from pylons import config

get_action = logic.get_action

import ckan.authz as authz
_check_access = logic.check_access
import ckan.lib.dictization.model_dictize as model_dictize

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

def group_list_authz(context, data_dict):
    '''Return the list of groups that the user is authorized to edit.
    :param available_only: remove the existing groups in the package
      (optional, default: ``False``)
    :type available_only: boolean
    :param am_member: if ``True`` return only the groups the logged-in user is
      a member of, otherwise return all groups that the user is authorized to
      edit (for example, sysadmin users are authorized to edit all groups)
      (optional, default: ``False``)
    :type am-member: boolean
    :returns: list of dictized groups that the user is authorized to edit
    :rtype: list of dicts
    '''
    model = context['model']
    user = context['user']
    available_only = data_dict.get('available_only', False)
    am_member = data_dict.get('am_member', False)
    group_type = data_dict.get('type', 'group')

    _check_access('group_list_authz', context, data_dict)

    sysadmin = authz.is_sysadmin(user)
    roles = authz.get_roles_with_permission('manage_group')
    if not roles:
        return []
    user_id = authz.get_user_id_for_username(user, allow_none=True)
    if not user_id:
        return []

    if not sysadmin or am_member:
        q = model.Session.query(model.Member) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.in_(roles)) \
            .filter(model.Member.table_id == user_id) \
            .filter(model.Member.state == 'active')
        group_ids = []
        for row in q.all():
            group_ids.append(row.group_id)

        if not group_ids:
            return []

    q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == False) \
        .filter(model.Group.state == 'active') \
        .filter(model.Group.type == group_type)

    if not sysadmin or am_member:
        q = q.filter(model.Group.id.in_(group_ids))

    groups = q.all()

    if available_only:
        package = context.get('package')
        if package:
            groups = set(groups) - set(package.get_groups())

    group_list = model_dictize.group_list_dictize(groups, context)
    return group_list