oer.validation = {};
oer.validation.rules = {};

oer.validation.rules.registration = {
  name: "required",
  username: "required",
  email: {
    required: true,
    email: true
  },
  confirm_email: {
    required: true,
    email: true,
    equalTo: "[name='email']"
  },
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

oer.validation.rules.profile = {
  name: "required",
  email: {
    required: true,
    email: true
  }
};

oer.validation.rules.change_password = {
  current_password: {
    required: true
  },
  new_password: {
    required: true,
    minlength: 5
  },
  confirm_new_password: {
    required: true,
    minlength: 5,
    equalTo: "[name='new_password']"
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

$.validator.setDefaults({
  errorPlacement: function(error, element) {
     error.appendTo(element.closest(".field").find(".errors"));
  }
});