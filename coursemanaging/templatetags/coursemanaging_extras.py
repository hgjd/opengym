from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter('duration')
def duration(value):
    total_seconds = int(value.total_seconds())
    days = value.days
    rest_seconds = total_seconds % 86400
    hours = rest_seconds // 3600
    minutes = (rest_seconds % 3600) // 60

    if days == 1:
        return '{} dag, {} uur en {} minuten'.format(days, hours, minutes)

    if days == 0 and minutes == 0:
        return '{} uur'.format(hours)

    if days == 0 and minutes != 0:
        return '{} uur en {} minuten'.format(hours, minutes)

    return '{} dagen, {} uur en {} minuten'.format(days, hours, minutes)
