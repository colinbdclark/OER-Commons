# -*- coding: utf-8 -*-

from visitcounts.models import VisitCounter


def count_visit(request, response, instance):
    VisitCounter.objects.count_item(request, response, instance)
