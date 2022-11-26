from django.core.paginator import Paginator
from django.conf import settings


def split_by_page(request, post):
    paginatir = Paginator(post, settings.POSTS_PER_PAGE)
    page_namber = request.GET.get('page')

    return paginatir.get_page(page_namber)
