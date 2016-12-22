var simpleBills = angular.module("SimpleBills", []);

simpleBills.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('#{').endSymbol('}');
});

simpleBills.controller("AddAccountController", function($scope) {
  $scope.formValidator = new CustomFormValidator({
    requiredFields: ['account_name'],
    submitBtnLoadingText: 'Creating ...'
  });
});

simpleBills.controller("SearchBillController", function($scope) {
    $scope.accountId = PageConfig ? PageConfig.accountId : "";
    $scope.accountTags = PageConfig ? PageConfig.accountTags : [];
    $scope.stats = PageConfig ? PageConfig.stats : {};
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

    var monthNames = moment.months();
    $scope.currentYear = moment().year();
    $scope.currentMonth = moment().month();
    $scope.currentMonthName = monthNames[$scope.currentMonth];

    $scope.setStartEndDates = function() {
      var startDay = moment([$scope.currentYear, $scope.currentMonth]).startOf('month').date();
      var endDay = moment([$scope.currentYear, $scope.currentMonth]).endOf('month').date();

      $scope.search_start_date = [$scope.currentYear, ($scope.currentMonth + 1), startDay].join('-');
      $scope.search_end_date = [$scope.currentYear, ($scope.currentMonth + 1), endDay].join('-');
    };

    $scope.setStartEndDates();

    $scope.selectedYearMonthsData = function() {
      return $scope.allYearsStats()[$scope.currentYear];
    };

    $scope.updateCurrentYearAndMonthsData = function() {
      $scope.setStartEndDates();
      $scope.monthsData = $scope.selectedYearMonthsData();
      $scope.fetchBills();
    };

    $scope.updateCurrentMonth = function(month, disabled) {
      if(disabled) {} else {
        $scope.currentMonth = month;
        $scope.setStartEndDates();
        $scope.currentMonthName = monthNames[month];
        $scope.fetchBills();
      }
    };

    $scope.allYearsStats = function() {
      var data = {};

      _.each($scope.getStatsYears(), function(year) {
        data[year] = [];
        _.each(moment.monthsShort(), function(m) { data[year].push({monthName: m, billCount: 0}); });
      });

      _.each($scope.stats.year_stats, function(yearStat) {
        var year = parseInt(yearStat.year);

        _.each(yearStat.month_stats, function(monthStat) {
          var month = parseInt(monthStat.month) - 1;
          data[year][month].billCount = parseInt(monthStat.bill_count);
        });

      });

      return data;
    };

    $scope.getStatsYears = function() {
      var years = [];

      _.each($scope.stats.year_stats, function(yearStat) {
        years.push(parseInt(yearStat.year));
      });

      years = _.uniq(years);

      var minYear = _.min(years);
      var maxYear = _.max(years);
      var ret = [minYear];

      var diff = moment([maxYear,0]).diff(minYear + '-01-01', 'years');

      _.times(diff, function(i) {
        ret.push(minYear + (i + 1));
      });

      return ret;
    };

    // Invoke init methods manually for the first time
    initDateRangePicker();
    $scope.fetchBills();
});

simpleBills.controller("AddBillController", function($scope) {
    $scope.accountId = PageConfig ? PageConfig.accountId : "";

    $scope.formValidator = new CustomFormValidator({
      requiredFields: ['bill_desc', 'bill_amount']
    });
});
