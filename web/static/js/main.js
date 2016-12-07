$(document).ready(function() {
    $(".collection-item").each(function() {
        if ($(this).attr("href") == location.pathname) {
            $(this).addClass("active");
        }
    });
    $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 30
    });
    $('.modal').modal();

    $('select').material_select();
    $('.datepicker').pickadate({
   selectMonths: true, 
   selectYears: 15
 })
});
