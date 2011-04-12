oer.newsletter = {};

oer.newsletter.init = function() {
  var $form = $("#newsletter-subscribe");
  $form.validate({rules: oer.validation.rules.newsletter});
};