IS_AUTHENTICATED = $("body").hasClass("authenticated");
HONEYPOT_FIELD_NAME = "address";

/* :econtains() filter for jQuery */
$.expr[":"].econtains = function(obj, index, meta, stack){
  return $.trim((obj.textContent || obj.innerText || $(obj).text() || "")).toLowerCase() == $.trim(meta[3]).toLowerCase();
}

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

DEFAULT_TOOLTIP_OPTIONS = {
    content: {
      text: function(api) {
        return $($(this).attr("rel"));
      },
      title: function(api) {
        return $(this).text();
      }
    },
    position: {
        my: "right center",
        at: "left center",
      target: "event"
    },
    style: {
      classes: "ui-tooltip-dark-blue ui-tooltip-shadow"
    }
};

RIGHTSIDE_TOOLTIP_OPTIONS = $.extend(true, {}, DEFAULT_TOOLTIP_OPTIONS, {
    position: {
        my: "left center",
        at: "right center"
    }
});
