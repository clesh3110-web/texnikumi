from django import template

register = template.Library()

@register.filter(name='dict_lookup')
def dict_lookup(dictionary, key):
    """Lug'atdan dinamik kalit bo'yicha qiymat olish"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
