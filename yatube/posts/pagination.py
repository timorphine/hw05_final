from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def paginator_context(queryset, request):
    page_number = request.GET.get('page')
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_obj = paginator.get_page(page_number)
    return page_obj
