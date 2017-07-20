from django import template

register = template.Library()


# filters
@register.filter
def available_tier_slots(tier, server):
    available = server.available_slots()
    val = int(available / tier.max_streams)
    return val if val else 0
