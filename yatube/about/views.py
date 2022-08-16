from django.views.generic.base import TemplateView


class author(TemplateView):
    template_name = "about/author.html"


class tech(TemplateView):
    template_name = "about/tech.html"
