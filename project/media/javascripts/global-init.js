$(function() {
    oer.search_box.init();
    $("label.inline").inlineLabel({
    showLabelEffect : "show",
    opacity : 1
    });
    oer.next_url.init();
    oer.login.init();
});

IS_AUTHENTICATED = $("body").hasClass("authenticated");