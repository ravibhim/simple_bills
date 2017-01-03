$(document).ready(function() {
    $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 30
    });
    $('.modal').modal();
    $('select').material_select();
    $('.dropdown-button').dropdown({
      inDuration: 300,
      outDuration: 225,
      constrain_width: false,
      hover: true ,
      gutter: 0,
      belowOrigin: true,
      alignment: 'right'
    }
  );

});
