from django.utils import timezone


def year(request):
    """Выводит значение текущего года"""
    year_now = timezone.now()
    return {
        'year': year_now.year
    }
