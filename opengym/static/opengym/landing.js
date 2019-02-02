(function ($) {
    "use strict"; // Start of use strict

    $('.carousel').carousel({
        interval: 12000
    });
    $('.close').click(function () {
        $('.custom-modal').hide();
    });


    // Smooth scrolling using jQuery easing
    $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function () {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: (target.offset().top - 54)
                }, 1000, "easeInOutExpo");
                return false;
            }
        }
    });

    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function () {
        $('.navbar-collapse').collapse('hide');
    });

    // Activate scrollspy to add active class to navbar items on scroll
    $('body').scrollspy({
        target: '#mainNav',
        offset: 60
    });

    $(document).on('click', '#weekToggle', function () {
        showWeekCalendar();
    });
    $(document).on('click', '#monthToggle', function () {
        showMonthCalendar();
    });

    $(window).on("resize", function () {
        if ($(window).width() > 600) {
            showMonthCalendar();
        } else {
            showWeekCalendar();
        }
    }).resize();

    $(document).on('click', '#week-prev', function () {
        if (!window.WEEK_CALENDAR_DAY) {
            window.WEEK_CALENDAR_DAY = getMonday(new Date());
        }
        window.WEEK_CALENDAR_DAY.setDate(window.WEEK_CALENDAR_DAY.getDate() - 7);
        console.log(window.WEEK_CALENDAR_DAY);
        var day = window.WEEK_CALENDAR_DAY.getDate();
        var month = window.WEEK_CALENDAR_DAY.getMonth() + 1;
        var year = window.WEEK_CALENDAR_DAY.getFullYear();
        $.ajax({
            type: 'GET',
            url: '/ajax-week-calendar/',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'month': month,
                'year': year,
                'day': day
            },
            success: function (data) {
                $('#calendar-week-content').html(data);
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });

    });
    $(document).on('click', '#week-next', function () {
        if (!window.WEEK_CALENDAR_DAY) {
            window.WEEK_CALENDAR_DAY = getMonday(new Date());
        }
        window.WEEK_CALENDAR_DAY.setDate(window.WEEK_CALENDAR_DAY.getDate() + 7);
        console.log(window.WEEK_CALENDAR_DAY);
        var day = window.WEEK_CALENDAR_DAY.getDate();
        var month = window.WEEK_CALENDAR_DAY.getMonth() + 1;
        var year = window.WEEK_CALENDAR_DAY.getFullYear();
        $.ajax({
            type: 'GET',
            url: '/ajax-week-calendar/',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'month': month,
                'year': year,
                'day': day
            },
            success: function (data) {
                $('#calendar-week-content').html(data);
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });

    });

    $(document).on('click', '#month-prev', function () {
        var month = window.CALENDAR_MONTH - 1;
        var year = window.CALENDAR_YEAR;
        if (window.CALENDAR_MONTH === 1) {
            month = 12;
            year = year - 1;
        }
        $.ajax({
            type: 'GET',
            url: '/ajax-calendar/',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'month': month,
                'year': year
            },
            success: function (data) {
                $('#calendar-content').html(data);
                window.CALENDAR_MONTH = month;
                window.CALENDAR_YEAR = year;
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });
    });

    $(document).on('click', '.month-next', function () {
        var month = window.CALENDAR_MONTH + 1;
        var year = window.CALENDAR_YEAR;
        if (window.CALENDAR_MONTH === 12) {
            month = 1;
            year = year + 1;
        }
        $.ajax({
            type: 'GET',
            url: '/ajax-calendar/',
            data: {
                'csrfmiddlewaretoken': window.CSRF_TOKEN,
                'month': month,
                'year': year
            },
            success: function (data) {
                $('#calendar-content').html(data);
                window.CALENDAR_MONTH = month;
                window.CALENDAR_YEAR = year;
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });
    });

    function showWeekCalendar() {
        $('#calendar-week-content').show();
        $('#weekToggle').hide();
        $('#calendar-content').hide();
        $('#monthToggle').show();
    }

    function showMonthCalendar() {
        $('#calendar-week-content').hide();
        $('#weekToggle').show();
        $('#calendar-content').show();
        $('#monthToggle').hide();
    }


})(jQuery); // End of use strict

function showImage(thumb_id) {
    var id = thumb_id.substring(10);
    var url = document.getElementById('url_' + id).innerHTML;
    var modalImg = document.getElementById('modal_image');
    modalImg.src = url;
    var modal = document.getElementById('modal-lightbox');
    modal.style.display = "block";
}

function getMonday(d) {
    d = new Date(d);
    var day = d.getDay(),
        diff = d.getDate() - day + (day == 0 ? -6 : 1); // adjust when day is sunday
    return new Date(d.setDate(diff));
}

