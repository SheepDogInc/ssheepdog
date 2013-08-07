import boto
import urllib2
import json

from django.views.generic import TemplateView
from django.utils.safestring import SafeString


class ListAWSPoliciesView(TemplateView):
    template_name = 'aws_policy_template.html'

    def get_context_data(self, **kwargs):
        def dry_helper(current_list, key, value):
            current_list[key].append(value)

        context = super(ListAWSPoliciesView, self).get_context_data(**kwargs)
        
        user_list = {}
        role_list = {}
        group_list = {}
        policy_list = {}

        iam = boto.connect_iam()
        for user in iam.get_all_users().list_users_result.users:
            user_list[user.user_name] = []
            for policy in iam.get_all_user_policies(user.user_name).list_user_policies_result.policy_names:
                dry_helper(user_list, user.user_name, policy)
                policy_list[policy] = urllib2.unquote(iam.get_user_policy(user.user_name, policy).policy_document)

        for role in iam.list_roles().list_roles_result.roles:
            role_list[role.role_name] = []
            for policy in iam.list_role_policies(role.role_name).policy_names:
                dry_helper(role_list, role.role_name, policy)
                policy_list[policy] = urllib2.unquote(iam.get_role_policy(role.role_name, policy).policy_document)

        for group in iam.get_all_groups().list_groups_result.groups:
            group_list[group.group_name] = []
            for policy in iam.get_all_group_policies(group.group_name).policy_names:
                dry_helper(group_list, group.group_name, policy)
                policy_list[policy] = urllib2.unquote(iam.get_group_policy(group.group_name, policy).policy_document)

        context.update({'user_policies': user_list,
                        'role_policies': role_list,
                        'group_policies': group_list,
                        'policies': SafeString(json.dumps(policy_list)),
                        })
        return context
