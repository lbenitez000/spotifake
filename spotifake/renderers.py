from rest_framework.renderers import JSONRenderer

class WrappedJSONRenderer(JSONRenderer):
    """
    This Renderer wraps array responses in a JSON object. The goal is to prevent attacks like:
    http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):

        # Only wrap the response is data is a list
        if isinstance(data, list):
            # Get the serializer from the view in renderer_context
            view = renderer_context.get('view')
            serializer = view.get_serializer()

            # Try to get the wrapper name defined in the serializer, use data as default.
            wrapper_name = getattr(serializer.Meta, 'wrapper_name', 'data')

            data = { wrapper_name: data }

        # Call the JOSNRenderer with the original data (possibly wrapped)
        json_data = super(WrappedJSONRenderer, self).render(data, accepted_media_type, renderer_context)

        return json_data