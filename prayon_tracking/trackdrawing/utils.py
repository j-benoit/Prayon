from django import template
from django.contrib.auth.models import Group
import datetime
import math
import numpy

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    return group in user.groups.all()

def datetime_to_radians(x):
    # radians are calculated using a 24-hour circle, not 12-hour, starting at north and moving clockwise
    time_of_day = x.time()
    seconds_from_midnight = 3600 * time_of_day.hour + 60 * time_of_day.minute + time_of_day.second
    radians = float(seconds_from_midnight) / float(12 * 60 * 60) * 2.0 * math.pi
    return radians

def average_angle(angles):
    # angles measured in radians
    x_sum = numpy.sum([math.sin(x) for x in angles])
    y_sum = numpy.sum([math.cos(x) for x in angles])
    x_mean = x_sum / float(len(angles))
    y_mean = y_sum / float(len(angles))
    return numpy.arctan2(x_mean, y_mean)

def radians_to_time_of_day(x):
    # radians are measured clockwise from north and represent time in a 24-hour circle
    seconds_from_midnight = int(float(x) / (2.0 * math.pi) * 12.0 * 60.0 * 60.0)
    hour = seconds_from_midnight / 3600
    minute = (seconds_from_midnight % 3600) / 60
    second = seconds_from_midnight % 60
    return datetime.time(hour, minute, second)

def average_times_of_day(x):
    # input datetime.datetime array and output datetime.time value
    angles = [datetime_to_radians(y) for y in x]
    avg_angle = average_angle(angles)
    return radians_to_time_of_day(avg_angle)


def remove_duplicate(string, separator='\n'):
    string_lines = set(string.split(separator))
    return separator.join(string_lines)
