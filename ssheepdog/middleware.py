import logging
from django.http import HttpResponseForbidden
from django.template import RequestContext, loader

class Templated403(object):
    """
    Replaces vanilla django.http.HttpResponseForbidden() responses
    with a rendering of 403.html
    """

    def process_response(self, request, response):
        if isinstance(response, HttpResponseForbidden):
            t = loader.get_template('403.html')
            return HttpResponseForbidden(t.render(RequestContext(request)))
        return response

class RequestLoggingMiddleware(object):
    logger = logging.getLogger('django.request')

    def process_request(self, request):
        message = 'Request received for %s' % request.path_info
        self.logger.debug(message, extra={'request': request})
