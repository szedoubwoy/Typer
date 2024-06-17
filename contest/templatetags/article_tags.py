# contest/templatetags/article_tags.py

from django import template
from ..models import Article

register = template.Library()

@register.simple_tag
def get_articles():
    return Article.objects.all()