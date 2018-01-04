(function($) {
  "use strict"; // Start of use strict

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

