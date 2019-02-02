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
                body = ['<div class="day-content">']

            if day in self.event_list:
                for event in self.event_list[day]:
                    body.append(
                        '<a href="%s" class="event-link">%s</a>' % (event.get_absolute_url(), event.event_name))

            if day in self.session_list:

                body.append('<ul class="calendar-day-events">')
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

            if day in self.building_day_list:
                for building_day in self.building_day_list[day]:
                    body.append('<a href="%s" class="building-icon"></a>' % building_day.get_absolute_url())

            if day in self.session_list or day in self.event_list or day in self.building_day_list:
                body.append('</div>')
                return self.day_cell(cssclass, '%s %s' % (day_html, ''.join(body)))

            return self.day_cell(cssclass, day_html)
        return self.day_cell('noday', '&nbsp;')

    def day_in_session_list(self, day):
        for day_key in self.session_list.keys():
            for event in self.session_list.get(day_key):
                if event.start.date() == day:
                    return True

    def day_in_building_list(self, day):
        for day_key in self.building_day_list.keys():
            for event in self.building_day_list.get(day_key):
                if event.start.date() == day:
                    return True

    def day_in_event_list(self, day):
        for day_key in self.event_list.keys():
            for event in self.event_list.get(day_key):
                if event.start.date() == day:
                    return True

    def formatday_week_view(self, day):
        day_html = '<div class="week-day-head">' + day_name[day.weekday()] + ' ' + str(day.day) + ' ' + month_name[
            day.month] + '</div>'
        cssclass = 'day day'
        if date.today() == date(day.year, day.month, day.day):
            cssclass += '-today'
        body = ['<div class="day-content">']
        filled = False
        if self.day_in_session_list(day) or self.day_in_building_list(day) or self.day_in_event_list(day):
            filled = True
            cssclass += '-filled'
            body = ['<div class="day-content">']

        if self.day_in_event_list(day):
            for event in self.event_list[day.day]:
                body.append(
                    '<a href="%s" class="event-link">%s</a>' % (event.get_absolute_url(), event.event_name))

        if self.day_in_session_list(day):
            body.append('<ul class="calendar-day-events">')
            for session in self.session_list[day.day]:
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

        if self.day_in_building_list(day):
            for building_day in self.building_day_list[day.day]:
                body.append('<a href="%s" class="building-icon"></a>' % building_day.get_absolute_url())

        if filled:
            body.append('</div>')
            return self.week_day_cell(cssclass, '%s %s' % (day_html, ''.join(body)))

        return self.week_day_cell(cssclass, day_html)

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
        return '<tr class="month-header"><th></th><th colspan="1"><span id="month-prev" class="fa fa-angle-left fa-2x month-nav month-prev"></span></th>' + \
               '<th colspan="3" class="calendar-month-title">%s</th>' % s + \
               '<th colspan="1"><span id="month-next" class="fa fa-angle-right fa-2x month-nav month-next"></span></th><th class="help-cell"><div class="legende"><h2>legende</h2><p class="event-link-legend"><span class="bd-ex"></span> Bouwdag</p><p class="session-subscribed">Ingeschreven voor les</p><p class="session-not-subscribed">Niet ingeschreven</p></div></th></tr>'

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

    def week_day_cell(self, cssclass, body):
        return '<div class="%s">%s</div>' % (cssclass, body)

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

    def bootstrap_week(self, year, month, day):
        """
        return weeken in a bootstrap container
        """
        self.year, self.month = year, month
        result_week = []
        for week in self.monthdatescalendar(year, month):
            for w_day in week:
                if w_day.day == day and w_day.month == month and w_day.year == year:
                    result_week = week

        result_html = []
        a = result_html.append
        a('<div class="calendar">')
        a('<div class="row week-head-row">')
        a(
            '<div class="col-2 text-center"><span id="week-prev" class="fa fa-angle-left fa-2x month-nav month-prev"></span></div>')
        a('<div class="col-8 week-head"><span> Week van '+str(result_week[0].day) + ' ' + month_name[result_week[0].month]+'</span></div>')
        a(
            '<div class="col-2 text-center"><span id="week-next" class="fa fa-angle-right fa-2x month-nav month-next"></span></div>')
        a('</div>')

        for result_day in result_week:
            a('<div>' + self.formatday_week_view(result_day) + '</div>')
        a('</div>')
        return ''.join(result_html)
