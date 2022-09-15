from django import template

register = template.Library()


@register.simple_tag()
def debug_users() -> list[tuple[str, str]]:
    return [('bob', 'Bob'), ('perry', 'Perry'), ('elliot', 'Elliot'), ('jd', 'JD'), ('turk', 'Turk'),
            ('carla', 'Carla'), ('janitor', 'Janitor'), ('jordan', 'Jordan'), ('ted', 'Ted'), ('gooch', 'Gooch')]
