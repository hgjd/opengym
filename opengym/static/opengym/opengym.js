(function($) {


$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

$(document).on("click", "button.remove-session", function () {
$('#remove-session').val($(this).attr("id"));
$('#remove-help').html($("#time-"+$(this).attr("id")).html());
});

$(document).on("click", "#id_max_students_diff_course",function(){
checkMaxStudents();
});

$(document).on("click", "#id_location_diff_course",function(){
checkLocation()
});




})(jQuery); // End of use strict

function checkMaxStudents(){
if ($('#id_max_students_diff_course').is(":checked")){
$('#div_id_max_students').slideDown();
}else{
$('#div_id_max_students').slideUp();
}
}

function checkLocation(){
if ($('#id_location_diff_course').is(":checked")){
$('#div_id_location_short').slideDown();
$('#div_id_location_street').slideDown();
$('#div_id_location_number').slideDown();
$('#div_id_location_city').slideDown();
}else{
$('#div_id_location_short').slideUp();
$('#div_id_location_street').slideUp();
$('#div_id_location_number').slideUp();
$('#div_id_location_city').slideUp();
}

}

function checkInvisibles(){
checkMaxStudents();
checkLocation();
}