oer.iframe_submission = {};

oer.iframe_submission.init = function() {
    oer.iframe_submission.dispatch();
};

oer.iframe_submission.dispatch = function() {
    var $container = $("#container");
    $container.empty();
    $container.addClass("loading");
    $container.load("/submit/dispatch", {
        "url" : RESOURCE_URL
    }, function(response) {
        $container.removeClass("loading");
    });
};

oer.iframe_submission.content_submission = {};

oer.iframe_submission.content_submission.init = function() {

    var $form = $("#content-submission");

    $form.stepy({
    block : true,
    validate : true,
    nextLabel : "Next",
    backLabel : "Back",
    finish : true
    });

    $form.find("fieldset.step p.content-submission-buttons a").button().css("visibility", "visible");
    $form.find(".button").button().css("visibility", "visible");

    $form.find("a.finish").button().css("visibility", "visible").click(function(e) {
        e.preventDefault();
        var $container = $form.parent();
        $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
                $form.hide();
                $container.find("ul.stepy-titles").hide();
                $container.append($("<p>" + response.message + "</p>"));
            }
        });
    });

    $license_type_radio = $form.find("input[name='license_type']");

    $.validator.addMethod("license_cc_old", function(value, element) {
        return $license_type_radio.filter(":checked").val() !== "cc-old" || value !== "-";
    }, "This field is required.");

    $form.validate({
        rules : {
        title : "required",
        abstract : "required",
        keywords : "required",
        general_subjects : "required",
        media_formats : "required",
        grade_levels : "required",
        geographic_relevance : "required",
        material_types : "required",
        license_cc : {
            required : function(el) {
                return $license_type_radio.filter(":checked").val() === "cc";
            }
        },
        license_cc_old : {
            license_cc_old : true
        },
        license_custom_name : {
            required : function(el) {
                return $license_type_radio.filter(":checked").val() === "custom";
            }
        },
        license_custom_url : "url"
        }
    });

    oer.content_submission.init_autocomplete();
    oer.autocomplete_list_widget.init();
    oer.content_submission.init_license();
    $form.show();
};

oer.iframe_submission.login = {};

oer.iframe_submission.login.init = function() {

    $form = $("#login");
    var $global_error_ct = $form.find(".errors.global");

    var validator = $form.validate({
    rules : {
    username : "required",
    password : "required"
    },
    submitHandler : function(form) {
        $global_error_ct.empty();
        $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
                oer.iframe_submission.dispatch();
                $("body").addClass("authenticated");
            } else if (response.status === "error") {
                if (response.errors.__all__ !== undefined) {
                    $global_error_ct.append('<label class="error">' + response.errors.__all__ + '</label>');
                    delete response.errors.__all__
                }
                validator.showErrors(response.errors);
            }
        });
        return false;
    }
    });

    $form.find(".buttons input").button();
};

oer.iframe_submission.existing_resource = {};

oer.iframe_submission.existing_resource.init = function() {
    
    function show_message($container, message) {
        $("<div></div>").addClass("message").text(message).hide().appendTo($container).fadeIn(300).delay(3000).fadeOut(1000, function() {
            $(this).remove();
        });
    }

    oer.rating.submit = function(e) {
        var $this = $(this);
        $.post("/rate", {
        number : $this.data("number"),
        identifier : $this.data("identifier")
        }, function(data) {
            if (data.status === "success") {
                var class_name = data.stars_class;
                $this.removeClass(oer.rating.get_class($this)).addClass(class_name);
                $this.data("initial_class", class_name);
                show_message($this.closest("div.item"), data.message);
            } else if (data.status === "error") {
                $this.removeClass(oer.rating.get_class($this)).addClass($this.data("initial_class"));
                show_message($this.closest("div.item"), data.message);
            }
        });
    };

    oer.tags_form.init();

    var $rate_form = $("form[name='rate']");
    var $show_rate_form_button = $("a.rate-item").button();

    $show_rate_form_button.click(function(e) {
        e.preventDefault();
        var $this = $(this);
        $rate_form.find("select").val("5");
        $rate_form.fadeIn(300);
        $this.hide();
    });

    $rate_form.find("a.cancel").click(function(e) {
        e.preventDefault();
        $rate_form.hide();
        $show_rate_form_button.show();
    });

    $rate_form.find("a.rate").click(function(e) {
        e.preventDefault();
        var $this = $(this);
        if ($rate_form.attr("method") == "post") {
            $.post($rate_form.attr("action"), {
                rating : $rate_form.find("select").val()
            }, function(response) {
                var $stars = $this.closest("div.rating").find("div.stars");
                $stars.removeClass().addClass("stars").addClass(response.stars_class);
                $rate_form.hide();
                $show_rate_form_button.show();
            });
        } else {
            $rate_form.submit();
        }
    });

    $review_form = $("form.review");
    var validator = $review_form.validate({
    rules : {
        text : "required"
    },
    submitHandler : function(form) {
        $.post($review_form.attr("action"), $review_form.serialize(), function(response) {
            if (response.status === "success") {
                var $message = $('<div class="message">' + response.message + '</div>').hide();
                $message.prependTo($review_form).fadeIn(300);
                setTimeout(function() {
                    $message.fadeOut(300, function() {
                        $message.detach();
                    });
                }, 3000);
            } else if (response.status === "error") {
                validator.showErrors(response.errors);
            }
        });
    }
    });

    var $review_btn = $review_form.find("a.submit").button().click(function(e) {
        e.preventDefault();
        $review_form.submit();
    });
};