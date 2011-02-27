from django import template
from django.core.cache import cache
from django.core.urlresolvers import resolve, reverse, Resolver404
from django.db.models import Count
from main.models import *
from datetime import datetime
import math

register = template.Library()

class GetTagsNode(template.Node):
    """
    Retrieves a list of live problem tags and places it into the context
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        tags = Tag.objects.all()
        context[self.varname] = tags
        return ''

def get_problem_tags(parser, token):
    """
    Retrieves a list of live problem tags and places it into the context
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError:
        raise template.TemplateSyntaxError('get_problem_tags syntax: {% get_problem_tags as varname %}')

    return GetTagsNode(args[2])
    
class GetCategoriesNode(template.Node):
    """
    Retrieves a list of problem categories and places it into the context
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        categories = Category.objects.all()
        context[self.varname] = categories
        return ''

def get_problem_categories(parser, token):
    """
    Retrieves a list of problem categories and places it into the context
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError:
        raise template.TemplateSyntaxError('get_problem_categories syntax: {% get_problem_categories as varname %}')

    return GetCategoriesNode(args[2])

class GetProblemsNode(template.Node):
    """
    Retrieves a set of problem objects.

    Usage::

        {% get_problems 5 as varname %}

        {% get_problems 5 as varname asc %}

        {% get_problems 1 to 5 as varname %}

        {% get_problems 1 to 5 as varname asc %}
    """
    def __init__(self, varname, count=None, start=None, end=None, order='desc'):
        self.count = count
        self.start = start
        self.end = end
        self.order = order
        self.varname = varname.strip()

    def render(self, context):
        # determine the order to sort the problems
        if self.order and self.order.lower() == 'desc':
            order = '-publish_date'
        else:
            order = 'publish_date'

        # get the live problems in the appropriate order
        problems = Problem.objectsorder_by(order).select_related()

        if self.count:
            # if we have a number of problems to retrieve, pull the first of them
            problems = problems[:int(self.count)]
        else:
            # get a range of problems
            problems = problems[(int(self.start) - 1):int(self.end)]

        # don't send back a list when we really don't need/want one
        if len(problems) == 1 and int(self.count) == 1 and not self.start:
            problems = problems[0]

        # put the problem(s) into the context
        context[self.varname] = problems
        return ''

def get_problems(parser, token):
    """
    Retrieves a list of Problem objects for use in a template.
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc in (4,6) or (argc in (5,7) and args[-1].lower() in ('desc', 'asc'))
    except AssertionError:
        raise template.TemplateSyntaxError('Invalid get_problems syntax.')

    # determine what parameters to use
    order = 'desc'
    count = start = end = varname = None
    if argc == 4: t, count, a, varname = args
    elif argc == 5: t, count, a, varname, order = args
    elif argc == 6: t, start, t, end, a, varname = args
    elif argc == 7: t, start, t, end, a, varname, order = args

    return GetProblemsNode(count=count,
                           start=start,
                           end=end,
                           order=order,
                           varname=varname)

class GetProblemArchivesNode(template.Node):
    """
    Retrieves a list of years and months in which problems have been posted.
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        cache_key = 'problem_archive_list'
        dt_archives = cache.get(cache_key)
        if dt_archives is None:
            archives = {}
            user = context.get('user', None)

            # iterate over all live problems
            for problem in Problem.objects.live(user=user).select_related():
                pub = problem.publish_date

                # see if we already have an problem in this year
                if not archives.has_key(pub.year):
                    # if not, initialize a dict for the year
                    archives[pub.year] = {}

                # make sure we know that we have an problem posted in this month/year
                archives[pub.year][pub.month] = True

            dt_archives = []

            # now sort the years, so they don't appear randomly on the page
            years = list(int(k) for k in archives.keys())
            years.sort()

            # more recent years will appear first in the resulting collection
            years.reverse()

            # iterate over all years
            for year in years:
                # sort the months of this year in which problems were posted
                m = list(int(k) for k in archives[year].keys())
                m.sort()

                # now create a list of datetime objects for each month/year
                months = [datetime(year, month, 1) for month in m]

                # append this list to our final collection
                dt_archives.append( ( year, tuple(months) ) )

            cache.set(cache_key, dt_archives)

        # put our collection into the context
        context[self.varname] = dt_archives
        return ''

def get_problem_archives(parser, token):
    """
    Retrieves a list of years and months in which problems have been posted.
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError:
        raise template.TemplateSyntaxError('get_problem_archives syntax: {% get_problem_archives as varname %}')

    return GetProblemArchivesNode(args[2])

def tag_cloud():
    """Provides the tags with a "weight" attribute to build a tag cloud"""

    cache_key = 'tag_cloud_tags'
    tags = cache.get(cache_key)
    if tags is None:
        MAX_WEIGHT = 7
        tags = Tag.objects.annotate(count=Count('problem'))

        if len(tags) == 0:
            # go no further
            return {}

        min_count = max_count = tags[0].problem_set.count()
        for tag in tags:
            if tag.count < min_count:
                min_count = tag.count
            if max_count < tag.count:
                max_count = tag.count

        # calculate count range, and avoid dbz
        _range = float(max_count - min_count)
        if _range == 0.0:
            _range = 1.0

        # calculate tag weights
        for tag in tags:
            tag.weight = int(MAX_WEIGHT * (tag.count - min_count) / _range)

        cache.set(cache_key, tags)

    return {'tags': tags}

def category_cloud():
    """Provides the tags with a "weight" attribute to build a tag cloud"""

    cache_key = 'category_cloud_tags'
    categories = cache.get(cache_key)
    if categories is None:
        MAX_WEIGHT = 7
        categories = Category.objects.annotate(count=Count('problem'))

        if len(categories) == 0:
            # go no further
            return {}

        min_count = max_count = categories[0].problem_set.count()
        for c in categories:
            if c.count < min_count:
                min_count = c.count
            if max_count < c.count:
                max_count = c.count

        # calculate count range, and avoid dbz
        _range = float(max_count - min_count)
        if _range == 0.0:
            _range = 1.0

        # calculate tag weights
        for c in categories:
            c.weight = int(MAX_WEIGHT * (c.count - min_count) / _range)

        cache.set(cache_key, categories)

    return {'categories': categories}

# register dem tags!
register.tag(get_problems)
register.tag(get_problem_tags)
register.tag(get_problem_categories)
register.tag(get_problem_archives)
register.inclusion_tag('main/_tag_cloud.html')(tag_cloud)
register.inclusion_tag('main/_category_cloud.html')(category_cloud)
