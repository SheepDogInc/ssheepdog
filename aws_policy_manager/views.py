import boto
import urllib2
import json

from django.views.generic import TemplateView
from django.utils.safestring import SafeString


class ListAWSPoliciesView(TemplateView):
    """
    This class builds three dictionaries for Users, Roles, and Groups with each
    element mapped to its associated policies. A fourth dictionary maps each
    policy name to its policy definition. This allows us to see who has which
    permissions on AWS without having to dig through Amazon's web interface.
    """
    template_name = 'aws_policy_template.html'

    def get_context_data(self, **kwargs):
        context = super(ListAWSPoliciesView, self).get_context_data(**kwargs)
        user_dict, role_dict, group_dict, policy_dict = ({} for i in range(4))
        iam = boto.connect_iam()

        def build_dict(current_list, key, policies, policy_function):
            current_list[key] = [policy for policy in policies.policy_names]
            for policy in policies.policy_names:
                policy_dict[policy] = urllib2.unquote(policy_function(key, policy).policy_document)

        for user in iam.get_all_users().list_users_result.users:
            build_dict(user_dict,
                       user.user_name,
                       iam.get_all_user_policies(user.user_name).list_user_policies_result,
                       iam.get_user_policy
                       )

        for role in iam.list_roles().list_roles_result.roles:
            build_dict(role_dict,
                       role.role_name,
                       iam.list_role_policies(role.role_name),
                       iam.get_role_policy
                       )

        for group in iam.get_all_groups().list_groups_result.groups:
            build_dict(group_dict,
                       group.group_name,
                       iam.get_all_group_policies(group.group_name),
                       iam.get_group_policy
                       )

        context.update({'user_policies': user_dict,
                        'role_policies': role_dict,
                        'group_policies': group_dict,
                        'policies': SafeString(json.dumps(policy_dict)),
                        })
        return context
