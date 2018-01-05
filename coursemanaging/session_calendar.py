from calendar import HTMLCalendar, day_name, month_name
from datetime import date
from itertools import groupby

from collections import defaultdict
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.html import conditional_escape as esc


class SessionCalendar(HTMLCalendar):
    def __init__(self, session_list, user):
        super(SessionCalendar, self).__init__()
        self.session_list = self.group_by_day(session_list)
        self.user = user

    def formatday(self, day, weekday):
        if day != 0:
            day_html = '<div class="day-head">' + str(day) + '</div>'
            cssclass = 'day'
            if date.today() == date(self.year, self.month, day):
                cssclass += '-today'
            if day in self.session_list:
                cssclass += '-filled'
                body = ['<ul class="calendar-day-events">']
                for session in self.session_list[day]:
                    body.append('<li>')
                    body.append('<time>')

                    if session.course.user_is_teacher(self.user):
                        body.append('<span class="fa fa-user-circle-o" aria-hidden="true"></span> ')

                    elif session.user_is_subscribed(self.user):
                        body.append('<span class="fa fa-check" aria-hidden="true"></span> ')

                    elif session.course.user_is_subscribed(self.user):
                        body.append('<span class="fa fa-thumb-tack" aria-hidden="true"></span> ')

                    else:
                        body.append('<span class="fa fa-bed" aria-hidden="true"></span> ')
                    body.append('%s</time>' % (
                        str(session.start_datetime.hour) + "h" + str(session.start_datetime.minute)))

                    body.append('<a href="%s">' % reverse('coursemanaging:session-detail', args=[session.id]))
                    body.append(session.course.course_name + '</a> <div style="clear: both;"></div>')

                    body.append('</li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%s %s' % (day_html, ''.join(body)))
            return self.day_cell(cssclass, day_html)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        self.year, self.month = theyear, themonth
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="calendar">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr class="month-header"><th colspan="1"><span class="fa fa-angle-left fa-2x month-nav month-prev"></span></th>' + \
               '<th colspan="5" class="calendar-month-title">%s</th>' % s + \
               '<th colspan="1"><span class="fa fa-angle-right fa-2x month-nav month-next"></span></th></tr>'

    def group_by_day(self, session_list):
        result = defaultdict()
        for session in session_list:
            if session.start_datetime.day not in result:
                result[session.start_datetime.day] = [session]
            else:
                result[session.start_datetime.day].append(session)
        for result_list in result.values():
            result_list.sort(key=lambda s: s.start_datetime)
        return result

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr class ="week-row-header">%s</tr>' % s

    def formatweekday(self, day):
        return '<th class="weekday">%s</th>' % (day_name[day])

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
        return '<tr class="week-row">%s</tr>' % s
