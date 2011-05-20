oer.profile = {};

oer.profile.init_profile_notification = function() {
    var $notification = $("#profile-notification");
    if (!$notification.length) {
        return;
    }
    var total_fields = $notification.data("total-fields");
    var cookie_name = $notification.data("cookie-name");
    $notification.find("div.close a").click(function(e) {
        e.preventDefault();
        var exdate = new Date();
        exdate.setDate(exdate.getDate() + 365);
        var cookie_value = escape(total_fields) + "; expires=" + exdate.toUTCString();
        document.cookie = cookie_name + "=" + cookie_value;
        $notification.remove();
    });
}

oer.profile.init_user_info = function() {
    var $form = $("form.user-info");
    var $header = $("table.profile th.user-info");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function(e) {
        $form.data("next", true);
    });
    $save_btn.data("label", $save_btn.val());
    var $inputs = $form.find(":input");
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
        if ($form.data("next")) {
            form.submit();
        } else {
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
    }
    });
};

oer.profile.init_change_password = function() {
    var $form = $("form.change-password");
    var $header = $("table.profile th.change-password");
    var $save_btn = $form.find("input[type='submit'].save");
    $save_btn.data("label", $save_btn.val());
    var $inputs = $form.find(":input");
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

oer.profile.init_geography = function() {
    var $form = $("form.geography");
    var $header = $("table.profile th.geography");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function(e) {
        $form.data("next", true);
    });
    var $inputs = $form.find(":input");
    $save_btn.data("label", $save_btn.val());
    var validator = $form.validate({
    rules : {},
    submitHandler : function(form) {
        if ($form.data("next")) {
            form.submit();
        } else {
            $header.addClass("loading");
            $save_btn.val("Saving...");
            var form_data = $form.serialize();
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
    }
    });

    // Map Widget
    if (window.google !== undefined && window.google.maps !== undefined) {

        var initial_location = new google.maps.LatLng(25, 0);

        var options = {
        zoom : 1,
        center : initial_location,
        mapTypeId : google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map"), options);
        var marker = null;
        var $select = $("select[name='country']");

        var place_marker = function(location, set_center) {
            if (set_center !== undefined && set_center) {
                map.setCenter(location);
            }
            if (marker === null) {
                marker = new google.maps.Marker({
                map : map,
                position : location
                });
            } else {
                marker.setPosition(location);
            }
        };

        var geocode_country = function(country_name) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({
                'address' : country_name
            }, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    place_marker(results[0].geometry.location, true);

                } else {
                    if (window.console !== undefined) {
                        console.log("Geocode was not successful for the following reason: " + status);
                    }
                }
            });
        };

        // Select country from dropdown list
        var select_country = function() {
            var $selected = $select.find("option:selected");
            if ($selected.val() !== "") {
                var country_name = $selected.text();
                geocode_country(country_name);
            } else {
                map.setCenter(initial_location);
            }

        };

        $select.change(function(e) {
            select_country();
        });
        select_country();

        // Pick country on map widget
        var pick_country = function(location) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({
                'latLng' : location
            }, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    place_marker(results[0].geometry.location);
                    var address_components = results[0].address_components;
                    for ( var i = 0; i < address_components.length; i++) {
                        var component = address_components[i];
                        if (component.types[0] === "country") {
                            var code = component.short_name;
                            $select.unbind("change");
                            $select.val(code);
                            $select.change(function(e) {
                                select_country();
                            });
                            break;
                        }
                    }
                    ;
                } else {
                    if (window.console !== undefined) {
                        console.log("Geocode was not successful for the following reason: " + status);
                    }
                }
            });
        };

        google.maps.event.addListener(map, 'click', function(e) {
            pick_country(e.latLng);
        });

    }

};

oer.profile.init_roles = function() {
    var $form = $("form.roles");
    var $header = $("table.profile th.roles");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function(e) {
        $form.data("next", true);
    });
    var $inputs = $form.find(":input");
    $save_btn.data("label", $save_btn.val());
    var validator = $form.validate({
    rules : {},
    submitHandler : function(form) {
        if ($form.data("next")) {
            form.submit();
        } else {
            $header.addClass("loading");
            $save_btn.val("Saving...");
            var form_data = $form.serialize();
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
    }
    });

    var $buttons_ct = $form.find("div.buttons");
    var $educator_header = $form.find("th.educator");
    var $educator_fields_ct = $form.find("td.educator");

    var $roles_input = $inputs.filter("[name='roles']");

    var EDUCATOR_ROLE_IDS = [ 1, 2 ];
    $roles_input.change(function(e) {
        var is_educator = false;
        $roles_input.filter(":checked").each(function(index, el) {
            var $el = $(el);
            var value = $el.val();
            if (is_educator) {
                return;
            }
            if (EDUCATOR_ROLE_IDS.indexOf(parseInt(value)) != -1) {
                is_educator = true;
            }
        });
        if (is_educator) {
            $buttons_ct.hide();
            $buttons_ct.fadeIn(300);
            $educator_header.fadeIn(300);
            $educator_fields_ct.fadeIn(300);
        } else {
            $buttons_ct.fadeOut(300, function() {
                $buttons_ct.fadeIn(300)
            });
            $educator_header.fadeOut(300);
            $educator_fields_ct.fadeOut(300);
        }
    });
};

oer.profile.init_wish = function() {
    var $form = $("form.wish");
    var $header = $("table.profile th.wish");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function(e) {
        $form.data("next", true);
    });
    var $inputs = $form.find(":input");
    $save_btn.data("label", $save_btn.val());
    var validator = $form.validate({
    rules : {},
    submitHandler : function(form) {
        if ($form.data("next")) {
            form.submit();
        } else {
            $header.addClass("loading");
            $save_btn.val("Saving...");
            var form_data = $form.serialize();
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
    }
    });
};
