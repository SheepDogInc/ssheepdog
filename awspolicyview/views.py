import boto
from django.views.generic import TemplateView


class ListAWSPoliciesView(TemplateView):
    template_name = 'aws_policy_template.html'

    def get_context_data(self, **kwargs):
        context = super(ListAWSPoliciesView, self).get_context_data(**kwargs)
        context['aws'] = 'lol'

        policy_list = {}

        iam = boto.connect_iam()
        for user in iam.get_all_users().list_users_result.users:
            for policy in iam.get_all_user_policies(user.user_name).list_user_policies_result.policy_names:
                try:
                    policy_list[user.user_name] += ', %s' % policy
                except KeyError:
                    policy_list[user.user_name] = policy


        context['user_policies'] = policy_list

        context.update()
        return context
