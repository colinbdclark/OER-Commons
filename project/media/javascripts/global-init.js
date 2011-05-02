$(function() {
    oer.search_box.init();
    $("label.inline").inlineLabel({
    showLabelEffect : "show",
    opacity : 1
    });
    oer.next_url.init();
    oer.login.init();

    // Google Analytics tracker to count logged in visitors.
    if (_gaq !== undefined) {
        var user_type = $("body").hasClass("authenticated") ? "Member" : "Anonymous";
        _gaq.push([ '_setCustomVar', 3, 'User Type', user_type, 2 ]);
    }
});
