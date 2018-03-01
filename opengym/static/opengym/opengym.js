(function($) {

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

$(document).on("click", "button.remove-session", function () {
$('#remove-session').val($(this).attr("id"));
$('#remove-help').html($("#time-"+$(this).attr("id")).html());
});


})(jQuery); // End of use strict

