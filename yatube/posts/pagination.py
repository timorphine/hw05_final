from django.core.paginator import Paginator


def paginator_context(queryset, request):
    page_number = request.GET.get('page')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }


def paginator_context_follow(queryset, request):
    page_number = request.GET.get('page')
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }
