IS_AUTHENTICATED = $("body").hasClass("authenticated");
HONEYPOT_FIELD_NAME = "address"; 
    
$(function() {
    oer.search_box.init();
    $("label.inline").inlineLabel({
    showLabelEffect : "show",
    opacity : 1
    });
    oer.next_url.init();
    oer.login.init();
    var $honeypot_field = $("input[name='" + HONEYPOT_FIELD_NAME + "']");
    if ($honeypot_field.length) {
        $.post("/honeypot/", function(data) {
            $honeypot_field.val(data.value);
        });
    }
});

