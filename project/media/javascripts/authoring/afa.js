(function() {
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
    $(".oer-container").attr("itemscope", "");
    $(".oer-container").prepend('<meta itemprop="is-display-transformable" content="font-size font-face foreground-colour background-colour"/>');
  }
  
  addAfAToBody();
  summerizeAfA();
})();
