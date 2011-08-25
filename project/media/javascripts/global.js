IS_AUTHENTICATED = $("body").hasClass("authenticated");
HONEYPOT_FIELD_NAME = "address";

/* :econtains() filter for jQuery */
$.expr[":"].econtains = function(obj, index, meta, stack){
  return $.trim((obj.textContent || obj.innerText || $(obj).text() || "")).toLowerCase() == $.trim(meta[3]).toLowerCase();
}

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
