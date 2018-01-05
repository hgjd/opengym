
(function($) {

"use strict";
$(document).on('click', '.news-link', function(){
     var id = $(this).attr("id");
     var eElement = $(this);
     $( ".current-news" ).remove();
     $('<span class="fa fa-eye current-news" aria-hidden="true"></span>').insertBefore(eElement.children(":first"));
     $.ajax({
        type: 'POST',
        url: '/news/',
        data: {'csrfmiddlewaretoken': window.CSRF_TOKEN,
        'news_item_id':id,},
        success: function(data) {
            $('.news-item').html(data);
        },
        error: function(xhr, status, error) {
            alert(error);
        }
    });
});

})(jQuery);