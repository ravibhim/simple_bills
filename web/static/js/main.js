$(document).ready(function() {
    $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 30
    });
    $('.modal').modal();

    $('select').material_select();
    $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 15
    });
});
