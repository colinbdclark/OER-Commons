$(function() {
    oer.search_box.init();
    if (!Modernizr.input.placeholder) {
        $.each($("input[placeholder][id]"), function(i, input) {
            var $input = $(input);
            var $label = $("<label>").addClass("inline").attr("for", $input.attr("id")).text($input.attr("placeholder")).insertAfter($input).inlineLabel({
            showLabelEffect : "show",
            opacity : 1
            });
        });
    }

    oer.next_url.init();
    oer.login.init();
    var $honeypot_field = $("input[name='" + HONEYPOT_FIELD_NAME + "']");
    if ($honeypot_field.length) {
        $.post("/honeypot/", function(data) {
            $honeypot_field.val(data.value);
        });
    }
    oer.profile.init_profile_notification();
});
