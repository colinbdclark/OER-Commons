var afa = afa || {};

(function() {

  afa.AfAProperties = {
      mouseAccess: {
          name: "is-mouse-accessible",
          type: "boolean",
          selector: ".mouse-access",
          summaryfunc: "fluid.identity"
      },
      kbdA11y: {
          name: "is-keyboard-accessible",
          type: "boolean",
          selector: ".kbd-access",
          summaryfunc: "afa.checkKbdA11y"
      },
      altText: {
          name: "has-alt-text",
          type: "boolean",
          selector: ".img-alt",
          summaryfunc: "afa.checkAltText"
      },
      dispTrans: {
          name: "is-display-transformable",
          type: "vocabulary",
          values: ["font-size", "font-face", "foreground-colour", "background-colour"],
          selector: ".disp-trans",
          summaryfunc: "afa.checkDispTrans"
      },
      hazard: {
          name: "hazard",
          type: "vocabulary",
          values: ["flashing", "olfactory", "motion"],
          selector: ".hazard",
          summaryfunc: "fluid.identity"
      }
  };

  // Propsed structure for the mapping btw each AfA property status and its tooltip text
  var tooltipTextMapping = {
    altText: {
      green: "green text for img-alt %s",
      yellow: "yellow text for img-alt",
      red: "red text for img-alt",
      grey: "grey text for img-alt"
    },
    dispTrans: {
      green: "green text for disp-trans",
      yellow: "yellow text for disp-trans",
      red: "red text for disp-trans",
      grey: "grey text for disp-trans"
    },
    kbdA11y: {
        green: "It is possible to operate the resource using the keyboard only",
        yellow: "It may or may not be possible to operate parts of the resource using the keyboard only",
        red: "It is not possible to operate the resource using the keyboard only",
        grey: "Cannot determine whether it is possible to operate the resource using the keyboard only"
    }
  };

  afa.buildTooltipContent = function (string) {
      return "<ul><li>"+string+"</li></ul>"
  };

  afa.updateUI = function (selector, level, tooltipText) {
    $(".afa-summary "+selector).addClass(level);
  
    fluid.tooltip(".afa-summary " + selector, {
      content: function () {
          // TODO: The construction of the tooltip html will have to move earlier, since it
          //       will be more specific to the different properties
          return afa.buildTooltipContent(tooltipText);
      }
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
  afa.checkAltText = function (itemName, itemProperty) {
    var counterAllImg = $(".oer-container img").length;
    var counterImgWithAlt = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var counterImgWithoutAlt = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
      
    var level = (counterImgWithAlt == counterAllImg ? "green" :
                (counterImgWithAlt == 0 ? "red" : "yellow"));
    
    return {
      level: level,
      // TODO: Constructing tooltip text will become more complex, as we will combine multiple strings
      tooltipText: tooltipTextMapping[itemName][level]
    };
  };
  
  /**
   * Check on "display-transformable"
   */
  afa.checkDispTrans = function (itemName, itemProperty) {
    var counterAllDispTrans = afa.AfAProperties.dispTrans.values.length, tooltipText;
    
    var dispTransValue = $(".oer-container meta[itemprop='" + itemProperty.name + "']").attr("content");
    var counterDispTrans = dispTransValue.split(" ").length;

    var level = (counterDispTrans == counterAllDispTrans ? "green" :
                (counterDispTrans == 0 ? "red" : "yellow"));

    return {
      level: level,
      tooltipText: tooltipTextMapping[itemName][level]
    };
  };
  
  /**
   * Check on "display-transformable"
   */
  afa.checkKbdA11y = function (itemName, itemProperty) {
    var allItems = $(".oer-container meta[itemprop='" + itemProperty.name + "']");
    var accessbleItems = $("[content='true']", allItems);

    var itemsThatQualify = $(".oer-container, figure.embed.video");
    var total = itemsThatQualify.length;
    var haveProp = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "']").length;
    var yes = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
    var dunno = itemsThatQualify.length - haveProp;

    var level = (total == 0 ? "grey" : (yes == total ? "green" : (no == total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: tooltipTextMapping[itemName][level]
    };
  };
  
  // End of the functions that check on AfA properties
  
  /**
   * Loop thru all AfA items to check on grade.
   */
  afa.summerizeAfA = function () {
    var tooltipText, itemTagName;
    
    fluid.each(afa.AfAProperties, function(itemProperty, itemName) {
      var result = fluid.invokeGlobalFunction(itemProperty.summaryfunc, [itemName, itemProperty]);
      // TODO: This if is only because fluid.identity returns the first argument
      if (result !== itemName) {
          afa.updateUI(itemProperty.selector, result["level"], result["tooltipText"]);
      }
    });
  };
  
  afa.addAfAToBody = function () {
    var container = $(".oer-container");
    container.attr("itemscope", "");

    // TODO: These itemprop strings should not be hard-coded
    container.prepend('<meta itemprop="is-mouse-accessible" content="true"/>');
    container.prepend('<meta itemprop="is-keyboard-accessible" content="true"/>');
    container.prepend('<meta itemprop="is-display-transformable" content="' + afa.AfAProperties.dispTrans.values.join(" ") + '"/>');
    container.prepend('<meta itemprop="has-ebook" content="false"/>');
    container.prepend('<meta itemprop="hazard" content=""/>');
  }
  
  afa.addAfAToBody();
  afa.summerizeAfA();
})();

