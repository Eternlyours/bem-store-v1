import hashlib
import urllib

from django import template
from django.utils.safestring import mark_safe
from products.models import ProductUserAction

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.filter
def as_percentage_of(part, whole):
    try:
        return "%d%%" % (float(part) / float(whole) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return "0"



@register.filter
def gravatar_url(email, size=20):
    default = "https://www.minervastrategies.com/wp-content/uploads/2016/03/default-avatar.jpg"
    return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.lower().encode()).hexdigest(), urllib.parse.urlencode({'d': default, 's': str(size)}))


@register.filter
def gravatar(email, size=20):
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s" width="%d" height="%d">' % (url, size, size))


@register.filter
def get_rate_user(user, product):
    rate = ProductUserAction.objects.filter(product=product, user=user).first()
    if rate:
        return rate.rate
    else:
        return 0


@register.filter
def declination(val, words):
    value = abs(int(val)) % 100
    num = value % 10
    if value > 10 and value < 20:
        return f'{val} {words[2]}'
    if num > 1 and num < 5:
	    return f'{val} {words[1]}'
    if num == 1:
	    return f'{val} {words[0]}'
    return f'{val} {words[2]}'