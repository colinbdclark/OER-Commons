oer.login = {};

oer.login.LOGGED_IN_EVENT = "oer-login-logged-in";
oer.login.LOGGED_OUT_EVENT = "oer-login-logged-out";

//Check if user is authenticated.
oer.login.is_authenticated = function() {
  return $("body").hasClass("authenticated");
};

//Show login popup. Run optional callback function if user is logged in
//successfully.
oer.login.show_popup = function(callback) {
  var $popup = $("#login-popup");
  var $body = $("body");
  var $document = $(document);
  var $header_user_name = $("header.global span.user-name");
  if (!$popup.length) {
    $popup = $('<div id="login-popup"></div>').appendTo($body).dialog({
      modal: false,
      draggable: false,
      resizable: false,
      title: "Log in",
      width: 365,
      dialogClass: "loading dropdown",
      position: ["center", "top"],
      show: "fade",
      hide: "fade"
    });
    $popup.load("/login/form", function() {
      $popup.dialog("widget").removeClass("loading");
      var $form = $popup.find("form.login");
      $form.find("#id_password").showPasswordCheckbox();
      $form.find("a.cancel").click(function(e) {
        e.preventDefault();
        $popup.dialog("close");
      });
      $form.find(":input:first").focus();
      var $button = $form.find("input[type='submit']").button();
      var $global_error_ct = $form.find(".errors.global");
      $form.validate({
        rules: {
          username: "required",
          password: "required"
        },
        submitHandler: function() {
          $popup.dialog("widget").addClass("loading");
          $button.button("option", "label", "Logging in");
          $button.button("option", "disabled", true);
          $global_error_ct.empty();
          $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
              $header_user_name.text(response.user_name);
              $body.addClass("authenticated");
              $popup.dialog("close");
              if (callback !== undefined) {
                callback();
              }
              $document.trigger(oer.login.LOGGED_IN_EVENT);
            } else if (response.status === "error") {
              if (response.errors.__all__ !== undefined) {
                $global_error_ct.append('<label class="error">' + response.errors.__all__ + '</label>');
                delete response.errors.__all__;
              }
              $popup.dialog("widget").effect("bounce", {"direction": "left", "distance": 20}, 200);
            }
            $popup.dialog("widget").removeClass("loading");
            $button.button("option", "label", "Log in");
            $button.button("option", "disabled", false);
          });
          return false;
        }
      });
    });
  } else {
    $popup.dialog("open");
    $popup.find(":input:first").focus();
  }
};

//Check if user is authenticated before running specified callback function.
//Show login popup is user is not authenticated and run the callback if he
//logs in successfully.
oer.login.check_login = function(callback) {
  if (oer.login.is_authenticated()) {
    callback();
  } else {
    oer.login.show_popup(callback);
  }
};

oer.login.init = function() {
  if ($("body").hasClass("disable-login-popup")) {
    return;
  }

  $("header.global a.login").click(function(e) {
    e.preventDefault();
    oer.login.show_popup();
  });

  var $next_url_form = $("form[name='next-url']");
  $(document).delegate("a.require-login", "click", function(e) {
    if (oer.login.is_authenticated()) {
      return true;
    }
    e.preventDefault();
    var $this = $(this);
    oer.login.show_popup(function() {
      if ($this.hasClass("with-next-url")) {
        $next_url_form.attr("action", $this.attr("href"));
        $next_url_form.submit();
      } else {
        window.location = $this.attr("href");
      }
    });
  });
};
