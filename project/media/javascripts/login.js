oer.login = {};

oer.login.LOGGED_IN_EVENT = "oer-login-logged-in";
oer.login.LOGGED_OUT_EVENT = "oer-login-logged-out";

oer.login.init = function() {
    $("#header a.login").click(function(e) {
        e.preventDefault();
        oer.login.show_popup();
    });

    var $body = $("body");
    var $next_url_form = $("form[name='next-url']");
    $(document).delegate("a.require-login", "click", function(e) {
        if ($body.hasClass("authenticated")) {
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

oer.login.show_popup = function(callback) {
    var $popup = $("#login-popup");
    var $body = $("body");
    var $document = $(document);
    if (!$popup.length) {
        $popup = $('<div id="login-popup"></div>').appendTo($body).dialog({
        modal : true,
        draggable : false,
        resizable : false,
        title : "Log in",
        width : 265,
        dialogClass : "loading"
        });
        $popup.load("/login/form", function(response) {
            $popup.dialog("widget").removeClass("loading");
            var $form = $popup.find("form.login");
            var $button = $form.find("input[type='submit']").button();
            var $global_error_ct = $form.find(".errors.global");
            var validator = $form.validate({
            rules : {
            username : "required",
            password : "required"
            },
            submitHandler : function(form) {
                $popup.dialog("widget").addClass("loading");
                $button.button("option", "label", "Logging in");
                $button.button("option", "disabled", true);
                $global_error_ct.empty();
                $.post($form.attr("action"), $form.serialize(), function(response) {
                    if (response.status === "success") {
                        $body.addClass("authenticated");
                        $popup.dialog("close");
                        if (callback !== undefined) {
                            callback();
                        }
                        $document.trigger(oer.login.LOGGED_IN_EVENT);
                    } else if (response.status === "error") {
                        if (response.errors.__all__ !== undefined) {
                            $global_error_ct.append('<label class="error">' + response.errors.__all__ + '</label>');
                            delete response.errors.__all__
                        }
                        validator.showErrors(response.errors);
                    }
                    $popup.dialog("widget").removeClass("loading");
                    $button.button("option", "label", "Log in");
                    $button.button("option", "disabled", false);
                });
                return false;
            }
            });
            $popup.dialog();
        });
    } else {
        $popup.dialog("open");
    }
}

oer.login.check_login = function(callback) {
    var $body = $("body");
    if ($body.hasClass("authenticated")) {
        callback();
    } else {
        oer.login.show_popup(callback);
    }
}