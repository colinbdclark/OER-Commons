oer.content_submission = {};

oer.content_submission.init_autocomplete = function() {
    $("#id_institution").autocomplete({
        minLength: 2,
        source: "/autocomplete/materials/institution/name"
    });
    $("#id_collection").autocomplete({
        minLength: 2,
        source: "/autocomplete/materials/collection/name"
    });
    
    function split( val ) {
        return val.split( /,\s*/ );
    }
    function extractLast( term ) {
        return split( term ).pop();
    }
    
    $("#id_authors").autocomplete({
        source: function( request, response ) {
            $.getJSON( "/autocomplete/materials/author/name", {
                term: extractLast( request.term )
            }, response );
        },
        search: function() {
            // custom minLength
            var term = extractLast( this.value );
            if ( term.length < 2 ) {
                return false;
            }
        },
        focus: function() {
            // prevent value inserted on focus
            return false;
        },
        select: function( event, ui ) {
            var terms = split( this.value );
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push( ui.item.value );
            // add placeholder to get the comma-and-space at the end
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
        }
    });
};

oer.content_submission.init_license = function() {
  var $form = $("form.content-submission");
  var $license_type_buttons = $form.find("input[name='license_type']");

  var $cc_latest = $form.find("div.cc-latest").detach().insertAfter($license_type_buttons.filter("[value='cc']").closest("div.radio"));
  var $cc_old = $form.find("div.cc-old").detach().insertAfter($license_type_buttons.filter("[value='cc-old']").closest("div.radio"));
  var $custom_license = $form.find("div.custom-license");
  var $cc_latest_errors = $cc_latest.find("div.errors");
  var $cc_latest_name = $cc_latest.find("a.name");
  var $choose_cc_button = $cc_latest.find("span.choose").detach().insertAfter($license_type_buttons.filter("[value='cc']").closest("label"));
  var $cc_latest_url = $cc_latest.find("input[name='license_cc']");
  var $cc_selection_widget = $cc_latest.find("div.selection-widget");
  var $cc_selection_widget_loader = $cc_selection_widget.find("img.loader");
  
  $license_type_buttons.change(
    function() {
      var $this = $(this);
      var value = $this.val();
      $cc_latest.hide();
      $cc_old.hide();
      $custom_license.hide();
      if (value == "cc") {
        $cc_latest.fadeIn(300);
      } else if (value == "cc-old") {
        $cc_old.fadeIn(300);
      } else if (value == "custom") {
        $custom_license.fadeIn(300);
      }
    }
  );
  
  $choose_cc_button.click(
    function(e) {
      e.preventDefault();
      $cc_latest.show();
      $cc_old.hide();
      $custom_license.hide();
      $cc_latest_name.hide();
      $cc_latest_errors.find("label").remove();
      $license_type_buttons.val(["cc"]);
      $cc_selection_widget.fadeIn(300);
    }
  );
  
  $cc_selection_widget.find("input[name='issue']").click(
    function(e) {
      e.preventDefault();
      var data = {};
      $cc_selection_widget.find("select").each(
        function() {
          var $this = $(this);
          data[$this.attr("name")] = $this.val();
        }
      );
      $cc_latest_errors.find("label").remove();
      $cc_selection_widget_loader.show();
      $.post("/license-picker/issue/", data,
        function(data) {
          data = $.parseJSON(data);
          if (data.status == "error") {
            $("<label></label>").addClass("error").text(data.message).appendTo($cc_latest_errors);
          } else {
            $cc_latest_url.val(data.url);
            $cc_latest_name.text(data.name);
            $cc_latest_name.attr("href", data.url);
            $cc_latest_name.show();
            $choose_cc_button.show();
            $cc_selection_widget.hide();
          }
          $cc_selection_widget_loader.hide();
        },
        "application/json"
      );
    }
  );
  
};

oer.content_submission.init_derived_fields = function() {
  $("#id_derived").change(
    function() {
      var $this = $(this);
      if ($this.attr("checked")) {
        $("div.derived-fields").fadeIn(300);
      } else {
        $("div.derived-fields").fadeOut(300);
      }
    }
  );
};

oer.content_submission.init_prepostrequisites_fields = function() {
  $("#id_has_prerequisites").change(
    function() {
      var $this = $(this);
      if ($this.attr("checked")) {
        $("fieldset.prerequisites-fields").fadeIn(300);
      } else {
        $("fieldset.prerequisites-fields").fadeOut(300);
      }
    }
  );
  $("#id_has_postrequisites").change(
    function() {
      var $this = $(this);
      if ($this.attr("checked")) {
        $("fieldset.postrequisites-fields").fadeIn(300);
      } else {
        $("fieldset.postrequisites-fields").fadeOut(300);
      }
    }
  );
};

oer.content_submission.init_rss_fields = function() {
  $("#id_in_rss").change(
    function() {
      var $this = $(this);
      if ($this.attr("checked")) {
        $("div.rss-fields").fadeIn(300);
      } else {
        $("div.rss-fields").fadeOut(300);
      }
    }
  );
  $("input[name='rss_timestamp_0']").date_input();
};

$.datepicker.setDefaults({ 
    dateFormat: "mm.dd.yy"
});