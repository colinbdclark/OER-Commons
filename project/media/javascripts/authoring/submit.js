var SubmitStep = function (tool) {

  this.$step = $("#step-submit");

  var $currentLicense = $("div.current-license");
  var $licenseWidget = this.$step.find("div.license-widget");
  var $licenseImages = $currentLicense.find("div.images .license");

  var currentURL = $licenseWidget.find(":hidden[name$='_url']").val();
  var currentName = $licenseWidget.find(":hidden[name$='_name']").val();
  if (currentURL !== "" && currentName !== "") {
    $currentLicense.find("a").attr("href", currentURL).text(currentName).show();
    var license_classes = $licenseWidget.data("license-type").split("-");
    $licenseImages.addClass("hide");
    $.each(license_classes, function(i, cls) {
      $licenseImages.filter(".license-" + cls).removeClass("hide");
    });
  }

  $licenseWidget.find(":radio").change(function() {
    var derivatives = $licenseWidget.find("div.derivatives :radio:checked").val();
    var commercial = $licenseWidget.find("div.commercial :radio:checked").val();
    if (derivatives && commercial) {
      var data = {
        "cc-question-derivatives": derivatives,
        "cc-question-commercial": commercial
      };

      $currentLicense.block();
      $.post($licenseWidget.data("issue-url"), data, function(response) {
        if (response.status === "success") {
          var url = response["url"];
          var name = response["name"];
          $licenseImages.addClass("hide");
          $.each(response["license_classes"], function(i, cls) {
            $licenseImages.filter(".license-" + cls).removeClass("hide");
          });
          $currentLicense.find("a").attr("href", url).text(name).show();
          $licenseWidget.find(":hidden[name$='_url']").val(url);
          $licenseWidget.find(":hidden[name$='_name']").val(name);
        }
        $currentLicense.unblock();
      });
    }
  });
};
