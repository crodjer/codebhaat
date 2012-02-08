from django import template
import calendar

register = template.Library()

@register.filter(name='month_name')
# Create a custom filter to convert month number to name
def month_name(month_number):
  return calendar.month_name[month_number][0:3].lower()


