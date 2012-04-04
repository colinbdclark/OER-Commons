(function () {
  var tooltipTextMapping = {
    "img-alt": {
      "green": "green text for img-alt %s",
      "yellow": "yellow text for img-alt",
      "red": "red text for img-alt",
      "grey": "grey text for img-alt"
    },
    "disp-trans": {
      "green": "green text for disp-trans",
      "yellow": "yellow text for disp-trans",
      "red": "red text for disp-trans",
      "grey": "grey text for disp-trans"
    }
  };
  
  var updateUI = function (itemTagName, description, tooltipText) {
    $(".afa-summary ." + itemTagName).text(description);
    
    fluid.tooltip(".afa-summary ." + itemTagName, {
      content: tooltipText
    });
    
  }
  var summerizeAfA = function () {
    var tooltipText, itemTagName;
    
    // image alt text
    itemTagName = "img-alt";
    
    var counterAllImg = $(".oer-container img").length;
    var counterImgWithAlt = $(".oer-container img").parent().children("meta[itemprop='has-alt-text'][content='true']").length;
    var counterImgWithoutAlt = $(".oer-container img").parent().children("meta[itemprop='has-alt-text'][content='false']").length;
    
    var description = "all: " + counterAllImg + "; has alt: " + counterImgWithAlt + "; no alt: " + counterImgWithoutAlt;
    
    tooltipText = tooltipTextMapping[itemTagName]["green"];
    
    updateUI(itemTagName, description, tooltipText);

    // body display transformable
    itemTagName = "disp-trans";

    var counterAllDispTrans = 4;
    var dispTransValue = $(".oer-container meta[itemprop='is-display-transformable']").attr("content");
    var counterDispTrans = dispTransValue.split(" ").length;

    description = counterDispTrans + " out of " + counterAllDispTrans + " are available.";

    if (counterDispTrans === counterAllDispTrans) {
      tooltipText = tooltipTextMapping[itemTagName]["green"];
    } else {
        tooltipText = tooltipTextMapping[itemTagName]["grey"];
    }

    updateUI(itemTagName, description, tooltipText);
  };
  
  var addAfAToBody = function () {
    $(".oer-container").attr("itemscope", "");
    $(".oer-container").prepend('<meta itemprop="is-display-transformable" content="font-size font-face foreground-colour background-colour"/>');
  }
  
  addAfAToBody();
  summerizeAfA();
})();
