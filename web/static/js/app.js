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
      $scope.determineTheMonthToShow();
      $scope.fetchBills();
    };

    $scope.determineTheMonthToShow = function() {
       // select the months that has bills
       var data = _.filter($scope.monthsData, function(m) { return m.billCount > 0; });

       if (data.length > 0) {
         var preSelectedMonth;
         // If the selected year is the current year then pre-select the current month
         if ($scope.currentYear == moment().year()) {
           preSelectedMonth = moment().month();
         } else {
           // Pre-select the month based on the available data for that particular year
           preSelectedMonth = moment().month(data[0].monthName).month();
         }

         $scope.updateCurrentMonth(preSelectedMonth, false);
       }
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

      // Add current year by default
      years.push(moment().year());

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
    $scope.fetchBills();
});

simpleBills.controller("AddBillController", function($scope) {
    $scope.accountId = PageConfig ? PageConfig.accountId : "";

    $scope.formValidator = new CustomFormValidator({
      fields: [
        'bill_desc', 'bill_amount', 'filename',
        'bill_currency_code','bill_date', 'bill_tags'
      ],
      requiredFields: ['bill_desc', 'bill_amount'],
      selectFields: ['bill_currency_code'],
      checkboxFields: ['bill_tags']
    });

    var ajaxFunc = function($form) {
      var params = new FormData();

      _.each(
        _.difference(
          $scope.formValidator.fields,
          $scope.formValidator.checkboxFields,
          $scope.formValidator.selectFields
        ),
        function(field) {
          params.set(field, $form.find('input[name="'+ field + '"]').val());
        }
      );

      _.each(
        $scope.formValidator.selectFields,
        function(field) {
          params.set(field, $form.find('select[name="'+ field + '"]').val());
        }
      );

      _.each($scope.formValidator.checkboxFields, function(field) {
        var values = [];

        _.each($form.find('input[name="'+ field + '"]:checked'), function($ele){
          values.push($($ele).val());
        });

        params.set(field, values);
      });

      var file = $form.find('input[name=filename]')[0].files[0];
      if(file) {
        params.set('filename', file, file.name);
      };

      // POST params
      $.ajax({
        type: 'POST',
        url: '/account/' + $scope.accountId + '/create_bill',
        data: params,
        contentType: false,
        cache: false,
        processData: false,
        statusCode: {
          302: function(xhr) {
            console.log('redirect the page');
          }
        }
      }).done(function(response) {
          $form.find('.modal').modal('close');
          $scope.formValidator.resetForm();

          var date = params.get('bill_date').split('/');
          $scope.$parent.currentYear = parseInt(date[2]);
          $scope.$parent.currentMonth = parseInt(date[0]);
          $scope.$parent.updateCurrentYearAndMonthsData();
          //console.log('success!!', response);
      }).fail(function(err) {
          console.log('err!!', err);
      });
    };

    $scope.formValidator.ajaxForm = function($event) {
      $event.preventDefault();

      if($scope.formValidator.validateFields()) {
        var $submitBtn = $($event.currentTarget);
        $submitBtn.addClass('disabled');
        $submitBtn.html($scope.formValidator.submitBtnLoadingText);

        if (!$scope.formValidator.$form) {
          $scope.formValidator.$form = $submitBtn.closest('form');
        }

        ajaxFunc($scope.formValidator.$form);
      } else {
        $scope.formValidator.highlightRequiredFields();
      }
    };
});
