(function() {

  // Proposed structure for property names; not yet used
  var AfAProperties = {
      alttext: {
          name: "has-alt-text",
          type: "boolean",
          selector: ".img-alt"
      },
      hazard: {
          name: "hazard",
          type: "vocabulary",
          values: ["flashing", "olfactory", "motion"]
      }
  };

  var summerizeAfA = function () {
    // image alt text
    var counterAllImg = $(".oer-container img").length;
    var counterImgWithAlt = $(".oer-container img").parent().children("meta[itemprop='has-alt-text'][content='true']").length;
    var counterImgWithoutAlt = $(".oer-container img").parent().children("meta[itemprop='has-alt-text'][content='false']").length;
    
    var description = "all: " + counterAllImg + "; has alt: " + counterImgWithAlt + "; no alt: " + counterImgWithoutAlt;
    
    $(".afa-summary .img-alt").text(description);
    
    fluid.tooltip(".afa-summary .img-alt", {
      content: description
    });
    
    // body display transformable
    var counterAllDispTrans = 4;
    var dispTransValue = $(".oer-container meta[itemprop='is-display-transformable']").attr("content");
    var counterDispTrans = dispTransValue.split(" ").length;

    description = counterDispTrans + " out of " + counterAllDispTrans + " are available.";

    $(".afa-summary .disp-trans").text(description);

    fluid.tooltip(".afa-summary .disp-trans", {
        content: description
      });
      
  };
  
  var addAfAToBody = function () {
    var container = $(".oer-container");
    container.attr("itemscope", "");

    // TODO: These itemprop strings should not be hard-coded
    container.prepend('<meta itemprop="is-mouse-accessible" content="true"/>');
    container.prepend('<meta itemprop="is-mouse-accessible" content="false"/>');
    container.prepend('<meta itemprop="is-display-transformable" content="font-size font-face foreground-colour background-colour"/>');
    container.prepend('<meta itemprop="has-ebook" content="false"/>');
    container.prepend('<meta itemprop="hazard" content=""/>');
  }
  
  addAfAToBody();
  summerizeAfA();
})();
