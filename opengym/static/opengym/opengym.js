(function ($) {


    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    $(document).on("click", "button.remove-session", function () {
        $('#remove-session').val($(this).attr("id"));
        $('#remove-help').html($("#time-" + $(this).attr("id")).html());
    });

    $(document).on("click", "#id_max_students_diff_course", function () {
        checkMaxStudents();
    });

    $(document).on("click", "#id_location_diff_course", function () {
        checkLocation();
    });

    $(document).on("click", "#id_multiple_sessions", function () {
        checkMultipleSessions();
    });

    $(document).on("click", ".close", function () {
        $('.custom-modal').hide();
    });


})(jQuery); // End of use strict


function checkMultipleSessions() {
    if ($('#id_multiple_sessions').is(":checked")) {
        $('#div_id_weekly_until').slideDown();
    } else {
        $('#div_id_weekly_until').slideUp();
    }
}

function checkMaxStudents() {
    if ($('#id_max_students_diff_course').is(":checked")) {
        $('#div_id_max_students').slideDown();
    } else {
        $('#div_id_max_students').slideUp();
    }
}

function checkLocation() {
    if ($('#id_location_diff_course').is(":checked")) {
        $('#div_id_location_short').slideDown();
        $('#div_id_location_street').slideDown();
        $('#div_id_location_number').slideDown();
        $('#div_id_location_city').slideDown();
    } else {
        $('#div_id_location_short').slideUp();
        $('#div_id_location_street').slideUp();
        $('#div_id_location_number').slideUp();
        $('#div_id_location_city').slideUp();
    }

}

function checkInvisibles() {
    checkMaxStudents();
    checkLocation();
}

function showImage(thumb_id) {
    var id = thumb_id.substring(10);
    var url = document.getElementById('url_' + id).innerHTML;
    var modalImg = document.getElementById('modal_image');
    modalImg.src = url;
    var modal = document.getElementById('modal-lightbox');
    modal.style.display = "block";
}