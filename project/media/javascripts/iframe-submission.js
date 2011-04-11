oer.iframe_submission = {};

oer.iframe_submission.init = function() {

    var $form = $("#content-submission");

    $form.stepy({
    block : true,
    validate : true,
    nextLabel : "Next",
    backLabel : "Back",
    finish : true
    });

    $form.find("fieldset.step p.content-submission-buttons a").button().css("visibility", "visible");
    $form.find(".button").button().css("visibility", "visible");

    $form.find("a.finish").button().css("visibility", "visible").click(function(e) {
        e.preventDefault();
        var $container = $form.parent(); 
        $.post($form.attr("action"), $form.serialize(), function(response) {
            if (response.status === "success") {
                $form.hide();
                $container.find("ul.stepy-titles").hide();
                $container.append($("<p>" + response.message + "</p>"));
            }
        });
    });

    $license_type_radio = $form.find("input[name='license_type']");

    $.validator.addMethod("license_cc_old", function(value, element) {
        return $license_type_radio.filter(":checked").val() !== "cc-old" || value !== "-";
    }, "This field is required.");

    $form.validate({
        rules : {
        title : "required",
        abstract : "required",
        keywords : "required",
        general_subjects : "required",
        media_formats : "required",
        grade_levels : "required",
        geographic_relevance : "required",
        material_types : "required",
        license_cc : {
            required : function(el) {
                return $license_type_radio.filter(":checked").val() === "cc";
            }
        },
        license_cc_old : {
            license_cc_old : true
        },
        license_custom_name : {
            required : function(el) {
                return $license_type_radio.filter(":checked").val() === "custom";
            }
        },
        license_custom_url : "url"
        }
    });

    $("a#close").click(function(e) {
        e.preventDefault();
        oer.iframe_submission.close();
    });

    oer.content_submission.init_autocomplete();
    oer.keywords_widget.init();
    oer.content_submission.init_license();

    $form.show();

};

oer.iframe_submission.close = function() {
    var parent_url = decodeURIComponent(document.location.hash.replace(/^#/, ''));
    XD.postMessage("close", parent_url, parent);
    return false;
};