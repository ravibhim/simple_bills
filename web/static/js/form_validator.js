var CustomFormValidator = function(config) {
  var self = this;
  self.submitBtnLoadingText = config.submitBtnLoadingText || 'Adding ...';
  self.requiredFields = config.requiredFields || [];
  self.requiredFieldsInputs = [];
  self.fields = config.fields || [];
  self.checkboxFields = config.checkboxFields || [];
  self.selectFields = config.selectFields || [];
  self.fieldsInputs = [];
  self.$form = null;

  for(var i = 0; i < self.fields.length; i++) {
    var $inputEle = $("input[ng-name='" + self.fields[i] + "'");
    self.fieldsInputs.push($inputEle);
  }

  for(var i = 0; i < self.requiredFields.length; i++) {
    var $inputEle = $("input[ng-model='" + self.requiredFields[i] + "'");
    self.requiredFieldsInputs.push($inputEle);
  }

  self.validateFields = function() {
    for(var i = 0; i < self.requiredFieldsInputs.length; i++) {
      if(!self.requiredFieldsInputs[i].val()) {
        return false;
      }
    }

    return true;
  };

  self.highlightRequiredFields = function() {
    for(var i = 0; i < self.requiredFieldsInputs.length; i++) {
      var $inputEle = self.requiredFieldsInputs[i];

      if(!$inputEle.val()) {
        $inputEle.addClass('invalid');
      } else {
        $inputEle.removeClass('invalid');
      }
    }
  };

  self.submitForm = function($event) {
    if(self.validateFields()) {
      var $submitBtn = $($event.currentTarget);
      $submitBtn.addClass('disabled');
      $submitBtn.html(self.submitBtnLoadingText);

      if (!self.$form) {
        self.$form = $submitBtn.closest('form');
      }

      self.$form.submit();
    } else {
      self.highlightRequiredFields();
    }
  };

  self.resetForm = function() {
    self.$form[0].reset();
    var $submitBtn = self.$form.find('button');
    $submitBtn.removeClass('disabled');
    $submitBtn.html("Add");
  };
};
