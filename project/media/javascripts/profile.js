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

oer.profile.init_avatar = function() {
    var $upload_btn = $("#upload-avatar-btn");
    var $avatar = $("section.avatar div.wrap");
    var $avatar_img = $avatar.find("img");
    var $delete_btn = $("#delete-avatar-btn");
    var $delete_btn_wrap = $delete_btn.closest("span");

    $upload_btn.upload({
        action: $upload_btn.attr("href"),
        onComplete: function(response) {
            response = $.parseJSON(response);
            if (response.status === "error") {
                oer.status_message.error(response.message, true);
            } else if (response.status === "success") {
                $avatar_img.attr("src", response.url);
                $delete_btn_wrap.show();
            }
            $avatar.removeClass("loading");
        },
        onSubmit: function() {
            $avatar.addClass("loading");
        }
    });
    $delete_btn.click(function(e) {
        e.preventDefault();
        $avatar.addClass("loading");
        $.post($delete_btn.attr("href"), function(response) {
            if (response.status === "error") {
                oer.status_message.error(response.message, true);
            } else if (response.status === "success") {
                $avatar_img.attr("src", response.url);
                $delete_btn_wrap.hide();
            }
            $avatar.removeClass("loading");
        });
    });
};

oer.profile.init_user_info = function() {
    var $form = $("form.user-info");
    var $header = $("table.profile th.user-info");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function() {
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
        submitHandler : function() {
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
    $next_btn.click(function() {
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

    var $country_field = $("#id_country");
    var $us_state_field = $("#id_us_state");
    var $us_state_field_ct = $("#id_us_state").parent().parent();
    var map = null;
    var initial_location = null;
    var geocode_address = null;

    // Map Widget
    if (window.google !== undefined && window.google.maps !== undefined) {

        initial_location = new google.maps.LatLng(25, 0);

        var options = {
            zoom : 1,
            center : initial_location,
            mapTypeId : google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map"), options);
        var marker = null;

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

        geocode_address = function(address) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({
                'address' : address
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

        // Pick country on map widget
        var pick_country = function(location) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({
                'latLng' : location
            }, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    place_marker(results[0].geometry.location);
                    var address_components = results[0].address_components;
                    for (var i = 0; i < address_components.length; i++) {
                        var component = address_components[i];
                        if (component.types[0] === "country") {
                            var code = component.short_name;
                            $country_field.unbind("change");
                            $country_field.val(code);
                            $country_field.change(function() {
                                select_country();
                                set_map_pin();
                            });
                            if (code === "US") {
                                $us_state_field_ct.show();
                            } else {
                                $us_state_field_ct.hide();
                            }
                        }
                        if (component.types[0] === "administrative_area_level_1") {
                            var code = component.short_name;
                            if ($us_state_field.find("option[value='" + code + "']").length) {
                                $us_state_field.unbind("change");
                                $us_state_field.val(code);
                                $us_state_field.change(function() {
                                    set_map_pin();
                                });
                            }
                        }
                    }
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

    // Select country from dropdown list
    var select_country = function() {
        var $selected = $country_field.find("option:selected");
        if ($selected.val() === "US") {
            $us_state_field_ct.show();
        } else {
            $us_state_field_ct.hide();
        }

    };

    var set_map_pin = function() {
        if (map == null) {
            return;
        }
        var $selected_country = $country_field.find("option:selected");
        if ($selected_country.val() === "") {
            map.setCenter(initial_location);
            return;
        }

        var address = $selected_country.text();
        if ($selected_country.val() === "US") {
            var $selected_state = $us_state_field.find("option:selected");
            if ($selected_state.val() !== "") {
                address = $selected_state.text() + " " + address;
            }
        }
        geocode_address(address);

    }

    $country_field.change(function() {
        select_country();
        set_map_pin();
    });

    $us_state_field.change(function() {
        set_map_pin();
    })

    set_map_pin();

};

oer.profile.init_roles = function() {
    var $form = $("form.roles");
    var $header = $("table.profile th.roles");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function() {
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

    var EDUCATOR_ROLE_IDS = [ 1, 2, 3 ];
    $roles_input.change(function() {
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

oer.profile.init_about = function() {
    var $form = $("form.about");
    var $header = $("table.profile th.about");
    var $save_btn = $form.find("input[type='submit'].save");
    var $next_btn = $form.find("input[type='submit'].next");
    $next_btn.click(function() {
        $form.data("next", true);
    });
    var $inputs = $form.find(":input");
    $save_btn.data("label", $save_btn.val());
    var validator = $form.validate({
        rules : {
            website_url: "url",
            facebook_id: {
                minlength: 5
            },
            skype_id: {
                minlength: 6
            }
        },
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
