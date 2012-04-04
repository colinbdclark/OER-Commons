(function() {

  // Proposed structure for property names; not yet used
  var AfAProperties = {
      altText: {
          name: "has-alt-text",
          type: "boolean",
          selector: ".img-alt"
      },
      dispTrans: {
          name: "is-display-transformable",
          type: "vocabulary",
          values: ["font-size", "font-face", "foreground-colour", "background-colour"],
          selector: ".disp-trans"
      },
      hazard: {
          name: "hazard",
          type: "vocabulary",
          values: ["flashing", "olfactory", "motion"]
      }
  };

  // Propsed structure for the mapping btw each AfA property status and its tooltip text
  var tooltipTextMapping = {
    "altText": {
      "green": "green text for img-alt %s",
      "yellow": "yellow text for img-alt",
      "red": "red text for img-alt",
      "grey": "grey text for img-alt"
    },
    "dispTrans": {
      "green": "green text for disp-trans",
      "yellow": "yellow text for disp-trans",
      "red": "red text for disp-trans",
      "grey": "grey text for disp-trans"
    }
  };

  var updateUI = function (itemTagName, description, tooltipText) {
    $(".afa-summary " + itemTagName).text(description);
  
    fluid.tooltip(".afa-summary " + itemTagName, {
      content: tooltipText
    });
  
  }

  /**
   * Each of these functions below check on one AfA property
   * @param itemName: the defined name to identify having alt text on the OER content
   *        itemProperty: the properties, including the used terminology or css selector, that 
   *                      associate with the AfA item
   * @returns A json string in the structure of 
   *          {
   *            "description": [string],
   *            "tooltipText": [string]
   *          }
   */
  
  /**
   * Check on the resources that require and have alt text, such as <img>
   */
  var checkAltText = function (itemName, itemProperty) {
    var counterAllImg = $(".oer-container img").length;
    var counterImgWithAlt = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var counterImgWithoutAlt = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
      
    var description = "all: " + counterAllImg + "; has alt: " + counterImgWithAlt + "; no alt: " + counterImgWithoutAlt;
    var tooltipText = tooltipTextMapping[itemName]["green"];
    
    return {
      "description": description,
      "tooltipText": tooltipText
    };
  };
  
  var checkDispTrans = function (itemName, itemProperty) {
    var counterAllDispTrans = 4, tooltipText;
    
    var dispTransValue = $(".oer-container meta[itemprop='" + itemProperty.name + "']").attr("content");
    var counterDispTrans = dispTransValue.split(" ").length;

    var description = counterDispTrans + " out of " + counterAllDispTrans + " are available.";

    if (counterDispTrans === counterAllDispTrans) {
      tooltipText = tooltipTextMapping[itemName]["green"];
    } else {
      tooltipText = tooltipTextMapping[itemName]["grey"];
    }
  
    return {
      "description": description,
      "tooltipText": tooltipText
    };
  };
  
  // End of the functions that check on AfA properties
  
  /**
   * Loop thru all AfA items to check on grade.
   */
  var summerizeAfA = function () {
    var tooltipText, itemTagName;
    
    fluid.each(AfAProperties, function(itemProperty, itemName) {
      var result;
      
      if (itemName === "altText") {
        result = checkAltText(itemName, itemProperty);
      } else if (itemName === "dispTrans") {
        result = checkDispTrans(itemName, itemProperty);
      }
      updateUI(itemProperty.selector, result["description"], result["tooltipText"]);
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
