(function ($) {
    if (location.hash) {
        var params = {}, queryString = location.hash.substring(1),
            regex = /([^&=]+)=([^&]*)/g, m;
        while (m = regex.exec(queryString)) {
            params[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
        }

        $.ajax({
            type: 'GET',
            url: '/catchtoken/',
            data: queryString,
            success: function (data) {
                window.location.replace(window.location.pathname);
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        })
    }
})(jQuery);