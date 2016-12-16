var simpleBills = angular.module("SimpleBills", []);

simpleBills.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('#{').endSymbol('}');
});

simpleBills.controller("SearchBillController", function($scope) {
    $scope.accountId = PageConfig ? PageConfig.accountId : "";
    $scope.accountTags = PageConfig ? PageConfig.accountTags.split(",") : [];
    $scope.bills = [];
    $scope.search_tags = {};

    var format_search_tags = function() {
        var tags = "";

        for (var tag in $scope.search_tags) {
            if ($scope.search_tags[tag] === true) {
                tags += "search_tags=" + tag + "&";
            }
        }

        return tags.slice(0, -1);
    };

    $scope.accountTags.forEach(function(tag) {
        $scope.search_tags[tag] = false;
    });

    $scope.fetchBills = function() {
        // Show the spinner
        $('#spinner-container').show();
        $.ajax({
            method: 'GET',
            url: "/account/" + $scope.accountId + "/search_bills?" + format_search_tags(),
            data: {
                search_query: $scope.search_query,
                search_start_date: $scope.search_start_date,
                search_end_date: $scope.search_end_date
            },
            success: function(data) {
                $scope.bills = data.results;
                $scope.$digest();
                $('#spinner-container').hide();
            },
            error: function() {
                location.reload();
            }
        });
    };

    $scope.searchOnEnterKey = function($event) {
      if ($event.keyCode == 13) {
        $scope.fetchBills();
      }
    };

    $scope.isTagSelected = function(tag) {
        return $scope.search_tags[tag];
    };

    var initDateRangePicker = function() {
        var start = moment().subtract(29, 'days');
        var end = moment();

        function showSelectedDate(start, end) {
            $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));

            $scope.search_start_date = start.format('YYYY-MM-DD');
            $scope.search_end_date = end.format('YYYY-MM-DD');

            $scope.fetchBills();
        }

        $('#reportrange').daterangepicker({
            startDate: start,
            endDate: end,
            opens: "left",
            ranges: {
                'Today': [moment(), moment()],
                'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'Last 30 Days': [moment().subtract(29, 'days'), moment()]
            }
        }, showSelectedDate);

        showSelectedDate(start, end);
    };

    initDateRangePicker();
    $scope.fetchBills();
});

simpleBills.controller("AddBillController", function($scope) {
    $scope.accountId = PageConfig ? PageConfig.accountId : "";
    $scope.requiredFields = ['bill_desc', 'bill_amount'];

    $scope.validateForm = function() {
      for(var i = 0; i < $scope.requiredFields.length; i++) {
        if(!$scope[$scope.requiredFields[i]]) {
          return false;
        }
      }

      return true;
    };

    $scope.highlightRequiredFields = function() {
      for(var i = 0; i < $scope.requiredFields.length; i++) {
        var field = $scope.requiredFields[i];
        var $inputEle = $("input[ng-model='" + field + "'");

        if(!$scope[field]) {
          $inputEle.addClass('invalid');
        } else {
          $inputEle.removeClass('invalid');
        }
      }
    };

    $scope.submitForm = function($event) {
      if($scope.validateForm()) {
        var $submitBtn = $($event.currentTarget);
        $submitBtn.addClass('disabled');
        $submitBtn.html('Saving ...');
        $submitBtn.closest('form').submit();
      } else {
        $scope.highlightRequiredFields();
      }
    };
});