oer.profile = {};

oer.profile.init_user_info = function() {
    var $form = $("form.user-info");
    var $header = $("table.profile th.user-info");
    var $save_btn = $form.find("input[type='submit'].save");
    $save_btn.data("label", $save_btn.val());
    var $inputs = $form.find("input");
    var validator = $form.validate({
    rules : {
    first_name : "required",
    last_name : "required",
    username : "required",
    email : {
    required : true,
    email : true
    }
    },
    submitHandler : function(form) {
        $header.addClass("loading");
        $save_btn.val("Saving...");
        var form_data = $form.serialize();
        $inputs.attr("disabled", "disabled");
        $.post($form.attr("action"), form_data, function(data) {
            if (data.status === "success") {
                oer.status_message.success(data.message, true);
            } else if (data.status === "error") {
                validator.showErrors(data.errors);
            }
            $header.removeClass("loading");
            $save_btn.val($save_btn.data("label"));
            $inputs.attr("disabled", "");
        });
    }
    });
};

oer.profile.init_change_password = function() {
    var $form = $("form.change-password");
    var $header = $("table.profile th.change-password");
    var $save_btn = $form.find("input[type='submit'].save");
    $save_btn.data("label", $save_btn.val());
    var $inputs = $form.find("input");
    var validator = $form.validate({
    rules : {
    current_password : {
        required : true
    },
    new_password : {
    required : true,
    minlength : 5
    },
    confirm_new_password : {
    required : true,
    minlength : 5,
    equalTo : "[name='new_password']"
    }
    },
    submitHandler : function(form) {
        $header.addClass("loading");
        $save_btn.val("Changing...");
        var form_data = $form.serialize();
        $inputs.attr("disabled", "disabled");
        $.post($form.attr("action"), form_data, function(data) {
            if (data.status === "success") {
                oer.status_message.success(data.message, true);
                $inputs.filter(":password").val("");
            } else if (data.status === "error") {
                validator.showErrors(data.errors);
            }
            $header.removeClass("loading");
            $save_btn.val($save_btn.data("label"));
            $inputs.attr("disabled", "");
        });
    }
    });
};
