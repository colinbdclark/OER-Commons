var afa = afa || {};

(function() {

  afa.AfAProperties = {
      mouseA11y: {
          name: "is-mouse-accessible",
          type: "boolean",
          selector: ".mouse-access",
          summaryfunc: "afa.checkA11y"
      },
      kbdA11y: {
          name: "is-keyboard-accessible",
          type: "boolean",
          selector: ".kbd-access",
          summaryfunc: "afa.checkA11y"
      },
      altText: {
          name: "has-alt-text",
          type: "boolean",
          selector: ".alt-text",
          summaryfunc: "afa.checkAltText"
      },
      dispTrans: {
          name: "is-display-transformable",
          type: "vocabulary",
          values: ["font-size", "font-face", "foreground-colour", "background-colour"],
          selector: ".disp-trans",
          summaryfunc: "afa.checkDispTrans"
      },
      ebook: {
          name: "has-ebook",
          type: "boolean",
          selector: ".ebook",
          summaryfunc: "afa.checkEbook"
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
    mouseA11y: {
      green: "It is possible to operate the resource using the mouse only",
      yellow: {
          yes: "It is possible to operate some parts of the resource using the mouse only",
          no: "It is not possible to operate some parts of the resource using the mouse only",
          dontknow: "For some parts of the resource, we cannot determine whether it is possible to operate it using the mouse only"
      },
      red: "It is not possible to operate the resource using the mouse only",
      grey: "Cannot determine whether it is possible to operate the resource using the mouse only"
    },
    kbdA11y: {
      green: "It is possible to operate the resource using the keyboard only",
      yellow: {
          yes: "It is possible to operate some parts of the resource using the keyboard only",
          no: "It is not possible to operate some parts of the resource using the keyboard only",
          dontknow: "For some parts of the resource, we cannot determine whether it is possible to operate it using the keyboard only"
      },
      red: "It is not possible to operate the resource using the keyboard only",
      grey: "Cannot determine whether it is possible to operate the resource using the keyboard only"
    },
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
    ebook: {
      green: "green text for ebook",
      yellow: "yellow text for ebook",
      red: "red text for ebook",
      grey: "grey text for ebook"
    }
  };

  /**
   * Build an HTML string suitable for display in the tooltip. Currently, this builds a bulleted list.
   * @param lines   either a single string or an object containing three strings
   * @param yes (optional) The number of resources positively identified for this property
   * @param no (optional) The number of resources negatively identified for this property
   * @param dontknow (optional) The number of resources undetermined for this property
   */
  afa.buildTooltipContent = function (lines, yes, no, dontknow) {
      // TODO: This is entirely not configurable
      if ((typeof lines) === 'string') {
          return "<ul><li>"+lines+"</li></ul>"
      }
      var string = "<ul>";
      if (yes > 0) {
          string += "<li>" + lines.yes + "</li>";
      }
      if (no > 0) {
          string += "<li>" + lines.no + "</li>";
      }
      if (dontknow > 0) {
          string += "<li>" + lines.dontknow + "</li>";
      }
      string += "</ul>";
      return string;
  };

  afa.updateUI = function (selector, level, tooltipText) {
    $(".afa-summary "+selector).addClass(level);
  
    fluid.tooltip(".afa-summary " + selector, {
      content: function () {
          return tooltipText;
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
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName][level], counterImgWithAlt, counterImgWithoutAlt)
    };
  };
  
  /**
   * Check on "display-transformable"
   */
  afa.checkDispTrans = function (itemName, itemProperty) {
    var numOfValsForEachDispTrans = afa.AfAProperties.dispTrans.values.length;
    var tooltipText;
    
    // Get expected number of dispTrans values
    var totalNumOfVideos = $(".oer-container figure.embed.video").length;
    var expectedDispTransVals = (totalNumOfVideos + 1) * numOfValsForEachDispTrans; // includes <body> + all videos

    // find number of display-transformable values on <body>
    var dispTransValue = $(".oer-container meta[itemprop='" + itemProperty.name + "']").attr("content");
    var counterDispTrans = dispTransValue.split(" ").length;

    // find number of display-transformable values on videos
    $(".oer-container figure.embed.video meta[itemprop='" + itemProperty.name + "']").each(function (index){
      var attrValue = $(this).attr("content");
      if (attrValue) {
        counterDispTrans += attrValue.split(" ").length;
      } else {
          counterDispTrans += 0;
      }
    });

    var level = (counterDispTrans == expectedDispTransVals ? "green" :
                (counterDispTrans == 0 ? "red" : "yellow"));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName][level], counterDispTrans)
    };
  };
  
  /**
   * Check on "display-transformable"
   */
  afa.checkA11y = function (itemName, itemProperty) {
    var allItems = $(".oer-container meta[itemprop='" + itemProperty.name + "']");
    var accessbleItems = $("[content='true']", allItems);

    var itemsThatQualify = $(".oer-container, figure.embed.video");
    var total = itemsThatQualify.length;
    var haveProp = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "']").length;
    var yes = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
    var dontknow = total - haveProp;

    var level = (total == 0 ? "grey" : (yes == total ? "green" : (no == total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName][level], yes, no, dontknow)
    };
  };
  
  /**
   * Check on "has-ebook"
   */
  afa.checkEbook = function (itemName, itemProperty) {
    // "has-ebook" only applies on <body>
    var total = 1;
    var yes = $(".oer-container meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = $(".oer-container meta[itemprop='" + itemProperty.name + "'][content='false']").length;

    var level = (yes === 0 && no === 0 ? "grey" : (yes == total ? "green" : (no == total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName][level], yes, no)
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
  
  afa.addAfAToEmbeddedVideo = function (figure) {
      // NOTE: These values are valid for currently-supported embedded youtube videos only
      // TODO: These itemprop names should not be hard-coded
      figure.attr("itemscope", "");
      figure.prepend('<meta itemprop="is-mouse-accessible" content="true"/>');
      figure.prepend('<meta itemprop="has-transcript" content="false"/>');
      figure.prepend('<meta itemprop="is-display-transformable" content=""/>');
  };

  // TODO: Should this call be somewhere else? in the save process, maybe?
  afa.addAfAToBody();


  afa.summerizeAfA();
})();

