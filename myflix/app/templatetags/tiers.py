from django import template

register = template.Library()


# filters
@register.filter
def available_tier_slots(tier, server):
    val = int(server.max_subscribers / tier.max_streams)
    return val if val else 0
