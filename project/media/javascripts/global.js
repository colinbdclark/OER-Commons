IS_AUTHENTICATED = $("body").hasClass("authenticated");
HONEYPOT_FIELD_NAME = "address";

/* :econtains() filter for jQuery */
$.expr[":"].econtains = function(obj, index, meta) {
  return $.trim((obj.textContent || obj.innerText || $(obj).text() || "")).toLowerCase() == $.trim(meta[3]).toLowerCase();
};

DEFAULT_TOOLTIP_OPTIONS = {
  content: {
    text: function() {
      return $($(this).attr("rel"));
    },
    title: function() {
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

TOPLEFTSIDE_TOOLTIP_OPTIONS = $.extend(true, {}, DEFAULT_TOOLTIP_OPTIONS, {
  position: {
    my: "right bottom",
    at: "left top"
  }
});

function rcorners($els) {
  // Apply rocon if it's installed. This actually happens only if we use IE.
  // All other browser use CSS for rounded corners.
  if (window.rocon) {
    $els.each(function(i, el) {
      window.rocon.update(el);
    });
  }
}
