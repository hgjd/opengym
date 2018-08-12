from calendar import HTMLCalendar, day_name, month_name
from collections import defaultdict
from datetime import date

from django.utils import timezone
from django.utils.timezone import localtime

timezone.activate(timezone.get_current_timezone())


class OpenCalendar(HTMLCalendar):
    def __init__(self, session_list, events, building_days, user):
        super(OpenCalendar, self).__init__()
        self.session_list = self.group_by_day(session_list)
        self.event_list = self.group_by_day(events)
        self.building_day_list = self.group_by_day(building_days)
        self.user = user

    def formatday(self, day, weekday):
        if day != 0:
            day_html = '<div class="day-head">' + str(day) + '</div>'
            cssclass = 'day day'
            if date.today() == date(self.year, self.month, day):
                cssclass += '-today'
            body = ['<div class="day-content">']

            if day in self.session_list or day in self.building_day_list or day in self.event_list:
                cssclass += '-filled'

            if day in self.session_list:
                body = ['<div class="day-content"><ul class="calendar-day-events">']
                for session in self.session_list[day]:
                    session_class = ""
                    if self.user.is_authenticated():
                        if session.course.user_is_teacher(self.user):
                            session_class = 'session-teacher'

                        elif session.user_is_subscribed(self.user):
                            session_class = 'session-subscribed'

                        elif session.course.user_is_subscribed(self.user):
                            session_class = 'session-course-subscribed'
                        else:
                            session_class = 'session-not-subscribed'
                    body.append('<li class="%s">' % session_class)
                    body.append('<time>')
                    body.append('%s' % (
                            str(localtime(session.start).hour) + "h" + "{:02d}".format(
                        localtime(session.start).minute)))

                    end = session.start + session.duration
                    body.append(' - %s</time>' % (
                            str(localtime(end).hour) + "h" + "{:02d}".format(
                        localtime(end).minute)))

                    body.append('<a href="%s">' % session.course.get_absolute_url())
                    body.append(session.course.course_name)
                    if session.location_diff_course and session.location_short:
                        body.append(" @ " + session.location_short)
                    elif session.course.location_short:
                        body.append(" @ " + session.course.location_short)
                    body.append('</a> <div style="clear: both;"></div>')
                    body.append('</li>')
                body.append('</ul>')

            if day in self.event_list:
                for event in self.event_list[day]:
                    body.append('<a href="%s" class="event-link">%s</a>' % (event.get_absolute_url(), event.event_name))

            if day in self.building_day_list:
                for building_day in self.building_day_list[day]:
                    body.append('<a href="%s" class="building-icon"></a>' % building_day.get_absolute_url())

            if day in self.session_list or day in self.event_list or day in self.building_day_list:
                body.append('</div>')
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
               '<th colspan="1"><span class="fa fa-angle-right fa-2x month-nav month-next"></span></th><th class="help-cell"><div class="legende"><h2>legende</h2><p class="event-link-legend">Event</p><p class="event-link-legend"><span class="bd-ex"></span> Bouwdag</p><p class="session-teacher">Je bent leerkracht</p><p class="session-subscribed">Ingeschreven voor les</p><p class="session-course-subscribed">Ingeschreven voor de lessenreeks, nog niet voor deze les</p><p class="session-not-subscribed">Niet ingeschreven</p></div></th></tr>'

    def group_by_day(self, entry_list):
        result = defaultdict()
        for session in entry_list:
            if localtime(session.start).day not in result:
                result[localtime(session.start).day] = [session]
            else:
                result[localtime(session.start).day].append(session)
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
