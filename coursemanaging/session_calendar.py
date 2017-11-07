from calendar import HTMLCalendar, day_name, month_name
from datetime import date
from itertools import groupby

from collections import defaultdict
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.html import conditional_escape as esc


class SessionCalendar(HTMLCalendar):
    def __init__(self, session_list):
        super(SessionCalendar, self).__init__()
        self.session_list = self.group_by_day_alt(session_list)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = 'day'
            if date.today() == date(self.year, self.month, day):
                cssclass += '-today'
            if day in self.session_list:
                cssclass += '-filled'
                body = ['<ul class="calendar-day-events">']
                for session in self.session_list[day]:
                    body.append('<li>')

                    body.append('<time>%s</time>' % (
                                str(session.start_datetime.hour) + "h" + str(session.start_datetime.minute)))
                    body.append('<a href="%s">' % reverse('coursemanaging:session-detail', args=[session.id]))
                    body.append(session.course.course_name + "</a>")
                    body.append('</li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
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
        return '<tr><th colspan="7" class="calendar-month-title">%s</th></tr>' % s

    def group_by_day(self, session_list):
        field = lambda session: session.start_datetime.day
        return dict(
            [(day, list(items)) for day, items in groupby(session_list, field)]
        )

    def group_by_day_alt(self, session_list):
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
