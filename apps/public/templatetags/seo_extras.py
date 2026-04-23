"""
Tags utilitaires pour le SEO.

{% capture_as var_name %}...{% endcapture_as %} rend le contenu du bloc
dans la variable `var_name` (utile pour définir une seule fois le titre
et le réutiliser dans <title>, og:title et twitter:title).
"""
from django import template

register = template.Library()


@register.tag(name="capture_as")
def do_capture_as(parser, token):
    try:
        _tag, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "Usage : {% capture_as <varname> %}...{% endcapture_as %}"
        )
    nodelist = parser.parse(("endcapture_as",))
    parser.delete_first_token()
    return CaptureNode(nodelist, varname)


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.nodelist.render(context).strip()
        return ""
