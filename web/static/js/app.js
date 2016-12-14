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
                window.reload();
            }
        });
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
