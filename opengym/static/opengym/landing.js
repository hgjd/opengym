(function($) {
  "use strict"; // Start of use strict

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
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
  $('.js-scroll-trigger').click(function() {
    $('.navbar-collapse').collapse('hide');
  });

  // Activate scrollspy to add active class to navbar items on scroll
  $('body').scrollspy({
    target: '#mainNav',
    offset: 54
  });

  $(document).on('click', '.month-prev', function(){
    var month = window.CALENDAR_MONTH-1;
    var year = window.CALENDAR_YEAR;
    if(window.CALENDAR_MONTH == 1){
    month = 12;
    year = year-1;
    }
     $.ajax({
        type: 'GET',
        url: '/ajax-calendar/',
        data: {'csrfmiddlewaretoken': window.CSRF_TOKEN,
        'month':month,
        'year':year},
        success: function(data) {
            $('#calendar-content').html(data);
            window.CALENDAR_MONTH=month;
            window.CALENDAR_YEAR=year;
        },
        error: function(xhr, status, error) {
            alert(error);
        }
    });
});

$(document).on('click', '.month-next', function(){
    var month = window.CALENDAR_MONTH+1;
    var year = window.CALENDAR_YEAR;
    if(window.CALENDAR_MONTH == 12){
     month = 1;
     year = year+1;
    }
     $.ajax({
        type: 'GET',
        url: '/ajax-calendar/',
        data: {'csrfmiddlewaretoken': window.CSRF_TOKEN,
        'month':month,
        'year':year,},
        success: function(data) {
            $('#calendar-content').html(data);
            window.CALENDAR_MONTH=month;
            window.CALENDAR_YEAR=year;
        },
        error: function(xhr, status, error) {
            alert(error);
        }
    });
});



})(jQuery); // End of use strict

