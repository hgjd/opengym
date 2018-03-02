from calendar import HTMLCalendar, day_name, month_name
from datetime import date

from collections import defaultdict


class SessionCalendar(HTMLCalendar):
    def __init__(self, session_list, user):
        super(SessionCalendar, self).__init__()
        self.session_list = self.group_by_day(session_list)
        self.user = user

    def formatday(self, day, weekday):
        if day != 0:
            day_html = '<div class="day-head">' + str(day) + '</div>'
            cssclass = 'day day'
            if date.today() == date(self.year, self.month, day):
                cssclass += '-today'
            if day in self.session_list:
                cssclass += '-filled'
                body = ['<ul class="calendar-day-events">']
                for session in self.session_list[day]:
                    body.append('<li>')
                    body.append('<time>')

                    if self.user.is_authenticated():
                        if session.course.user_is_teacher(self.user):
                            body.append('<span class="fa fa-user-circle-o" aria-hidden="true"></span> ')

                        elif session.user_is_subscribed(self.user):
                            body.append('<span class="fa fa-check" aria-hidden="true"></span> ')

                        elif session.course.user_is_subscribed(self.user):
                            body.append('<span class="fa fa-thumb-tack" aria-hidden="true"></span> ')

                        else:
                            body.append('<span class="fa fa-bed" aria-hidden="true"></span> ')

                    body.append('%s</time>' % (
                        str(session.start.hour) + "h" + str(session.start.minute)))

                    body.append('<a href="%s">' % session.course.get_absolute_url())
                    body.append(session.course.course_name)
                    if session.location_diff_course and session.location_short:
                        body.append(" @ "+session.location_short)
                    elif session.course.location_short:
                        body.append(" @ "+session.course.location_short)
                    body.append('</a> <div style="clear: both;"></div>')
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
        return '<tr class="month-header"><th></th><th colspan="1"><span class="fa fa-angle-left fa-2x month-nav month-prev"></span></th>' + \
               '<th colspan="3" class="calendar-month-title">%s</th>' % s + \
               '<th colspan="1"><span class="fa fa-angle-right fa-2x month-nav month-next"></span></th><th class="help-cell"><span class="fa fa-info-circle calendar-help" data-toggle="modal" data-target="#calendar-info-modal"></span></th></tr>'

    def group_by_day(self, session_list):
        result = defaultdict()
        for session in session_list:
            if session.start.day not in result:
                result[session.start.day] = [session]
            else:
                result[session.start.day].append(session)
        for result_list in result.values():
            result_list.sort(key=lambda s: s.start)
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
