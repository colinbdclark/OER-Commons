oer.validation = {};
oer.validation.rules = {};

oer.validation.rules.registration = {
  email: {
    required: true,
    email: true
  },
  password: {
    required: true,
    minlength: 5
  }
};

oer.validation.rules.reset_password_init = {
  email: {
    required: true,
    email: true
  }
};

oer.validation.rules.reset_password = {
  password: {
    required: true,
    minlength: 5
  },
  confirm_password: {
    required: true,
    minlength: 5,
    equalTo: "[name='password']"
  }
};

oer.validation.rules.save_search = {
  title: {
    required: true
  }
};

oer.validation.rules.send_this = {
  email: {
    required: true,
    email: true
  }
};

oer.validation.rules.newsletter = {
  email: {
    required: true,
    email: true
  }
};

$.validator.setDefaults({
  errorPlacement: function(error, element) {
    error.prependTo(element.closest(".input"));
  },
  errorElement: "span",
  errorClass: "help-block",
  highlight: function(element, errorClass, validClass) {
    $(element).closest(".input").parent().addClass("error");
  },
  unhighlight: function(element, errorClass, validClass) {
    $(element).closest(".input").parent().removeClass("error");
  },
  submitHandler: function(form) {
    if (!this.been_submited) {
      this.been_submitted = true;
      form.submit();
    } else {
      return false;
    }
  }
});
