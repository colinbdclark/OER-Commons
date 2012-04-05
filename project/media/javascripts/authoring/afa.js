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
      colourCode: {
          name: "uses-colour-coding ",
          type: "unknown",
          selector: ".colour-coding",
          summaryfunc: "afa.unknown"  // ToDo: needs an actual summary function eventually
      },
      hazard: {
          name: "has-hazard ",
          type: "unknown",
          selector: ".hazard",
          summaryfunc: "afa.unknown"  // ToDo: needs an actual summary function eventually
      },
      altText: {
        name: "has-alt-text",
        type: "boolean",
        selector: ".alt-text",
        summaryfunc: "afa.checkImgProp"
      },
      imgAudioAdapt: {
        name: "has-audio-representation",
        type: "boolean",
        selector: ".img-audio-adapt",
        summaryfunc: "afa.unknown"
      },
      imgLongDesc: {
        name: "has-long-description",
        type: "boolean",
        selector: ".img-long-desc",
        summaryfunc: "afa.unknown"
      },
      audioTrans: {
        name: "has-transcript",
        type: "boolean",
        selector: ".text-alt",
        summaryfunc: "afa.alwaysFalse"  // ToDo: needs an actual summary function eventually
      },
      audioVisualAdapt: {
        name: "has-visual-representation",
        type: "boolean",
        selector: ".audio-visual-adapt",
        summaryfunc: "afa.alwaysFalse"  // ToDo: needs an actual summary function eventually
      },
      videoAudioAdapt: {
        name: "has-audio-description",
        type: "boolean",
        selector: ".video-audio-adapt",
        summaryfunc: "afa.unknown"  // ToDo: needs an actual summary function eventually
      },
      videoVisualAdapt: {
        name: "has-visual-representation",
        type: "boolean",
        selector: ".video-visual-adapt",
        summaryfunc: "afa.unknown"  // ToDo: needs an actual summary function eventually
      }
  };

  // Propsed structure for the mapping btw each AfA property status and its tooltip text
  var tooltipTextMapping = {
    mouseA11y: {
      heading: "Mouse Access",
      green: "It is possible to use this learning resource using the mouse only.",
      yellow: {
          yes: "<don't know what to say about mouse-accessible stuff>",
          no: "The following parts cannot be used with the mouse only: some of the video players.",
          dontknow: "It may not be possible to use parts of this learning resource using the mouse only."
      },
      red: "It is not possible to use this learning resource using the mouse only.",
      grey: "Cannot determine if using this learning resource needs the mouse."
    },
    kbdA11y: {
      heading: "Keyboard Access",
      green: "It is possible to use this learning resource using the keyboard only.",
      yellow: {
          yes: "<don't know what to say about keyboard-accessible stuff>",
          no: "The following parts cannot be used with the keyboard only: some of the video players.",
          dontknow: "It may not be possible to use parts of this learning resource using the keyboard only."
      },
      red: "It is not possible to use this learning resource using the keyboard only.",
      grey: "Cannot determine if using this learning resource needs the keyboard."
    },
    dispTrans: {
      heading: "Display Transformability",
      green: "It is possible to transform the presentation and interface of this learning resource.",
      yellow: {
          yes: "?yes?",
          no: "The display of some of the video players in this resource cannot be transformed.",
          dontknow: "It may not be possible to transform the presentation and interface of parts of this learning resource."
      },
      red: "It is not possible to transform the presentation and interface of this learning resource.",
      grey: "Cannot determine if this learning resource's presentation and interface can be transformed."
    },
    ebook: {
      heading: "eBook Export",
      green: "?green?",
      yellow: "?yellow?",
      red: "Cannot download this learning resource as an eBook.",
      grey: "Cannot determine if this learning resource can be downloaded as an eBook."
    },
    colourCode: {
      heading: "Colour Coding",
      grey: "Cannot determine if this learning resource uses colour to convey information."
    },
    hazard: {
      heading: "Hazards",
      grey: "Cannot determine if this learning resource triggers any known hazards (e.g., seizures, nausea, etc.)."
    },
    altText: {
      heading: "Alt Text",
      green: "All images in this learning resource have alternative text.",
      yellow: {
          yes: "?yes?",
          no: "Some images in this learning resource have no alternative text.",
          dontknow: "It is possible that some images in this learning resource have no alternative text."
      },
      red: "No images in this learning resource have alternative text.",
      grey: "Cannot determine if the images in this learning resource have alternative text."
    },
    imgAudioAdapt: {
      heading: "Audio Adaptations",
      green: "?green?",
      yellow: "?yellow?",
      red: "No images in this learning resource are associated with audio descriptions.",
      grey: "Cannot determine if any images in this learning resource are associated with audio descriptions."
    },
    imgLongDesc: {
      heading: "Long Descriptions",
      green: "?green?",
      yellow: {
          yes: "?yes?",
          no: "Some images in this learning resource have no long descriptions.",
          dontknow: "It is possible that some images in this learning resource have no alternative text."
      },
      red: "No images in this learning resource are associated with long descriptions.",
      grey: "Cannot determine if the images in this learning resource have extended descriptions."
    },
    audioTrans: {
      green: "green text for audioTrans",
      yellow: "yellow text for audioTrans",
      red: "red text for audioTrans",
      grey: "grey text for audioTrans"
    },
    audioVisualAdapt: {
      heading: "Visual Adaptations",
      green: "green text for audioVisualAdapt",
      yellow: "yellow text for audioVisualAdapt",
      red: "No videos in this learning resource have visual adaptations for the audio track.",
      grey: "Cannot determine if the audio tracks for videos in this learning resource have visual adaptations."
    },
    videoAudioAdapt: {
      heading: "Audio Adaptations",
      green: "green text for videoAudioAdapt",
      yellow: "yellow text for videoAudioAdapt",
      red: "red text for videoAudioAdapt",
      grey: "Cannot determine if the videos in this learning resource have aural descriptions for the video track."
    },
    videoVisualAdapt: {
      heading: "Visual Adaptations",
      green: "green text for videoVisualAdapt",
      yellow: "yellow text for videoVisualAdapt",
      red: "red text for videoVisualAdapt",
      grey: "grey text for videoVisualAdapt"
    }
  };

  /**
   * Build an HTML string suitable for display in the tooltip. Currently, this builds a bulleted list.
   * @param lines   either a single string or an object containing three strings
   * @param yes (optional) The number of resources positively identified for this property
   * @param no (optional) The number of resources negatively identified for this property
   * @param dontknow (optional) The number of resources undetermined for this property
   */
  afa.buildTooltipContent = function (strings, level, yes, no, dontknow) {
      // TODO: This is entirely not configurable
      var string = "<h1>" + strings.heading + "</h1>";
      var lines = strings[level];
      if ((typeof lines) === 'string') {
          return string + "<ul><li>"+lines+"</li></ul>"
      }
      string += "<ul>";
/*
      if (yes > 0) {
          string += "<li>" + lines.yes + "</li>";
      }
*/
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
      },
      position: {
          my: "right center",
          at: "left center",
          offset: "0 0"
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
   * Check on AfA properties specifically used by <img>, for example, has-alt-text
   */
  afa.checkImgProp = function (itemName, itemProperty) {
    var total = $(".oer-container img").length;
    var yes = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = $(".oer-container img").parent().children("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
      
    var level = (yes === 0 && no === 0 && total !== 0 ? "grey" : (yes === total || total === 0 ? "green" : (no === total ? "red" : "yellow")));
    
    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, yes, no)
    };
  };
  
  /**
   * Check on "display-transformable"
   */
  afa.checkDispTrans = function (itemName, itemProperty) {
    var numOfValsForEachDispTrans = afa.AfAProperties.dispTrans.values.length;
    var tooltipText;
    var total = 0, yes = 0, no = 0;
    
    // Get expected number of dispTrans values
    var totalNumOfVideos = $(".oer-container figure.embed.video").length;
    var total = (totalNumOfVideos + 1) * numOfValsForEachDispTrans; // includes oer container + all videos

    // find number of display-transformable values on videos and oer container
    $(".oer-container, figure.embed.video").find("meta[itemprop='" + itemProperty.name + "']").each(function (index){
      var attrValue = $(this).attr("content");
      if (attrValue) {
        yes += attrValue.split(" ").length;
      } else {
          yes += 0;
      }
    });

    var level = (yes === total ? "green" : (yes === 0 ? "red" : "yellow"));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, yes)
    };
  };
  
  /**
   * Check on "mouse-access" and "kbd-access"
   */
  afa.checkA11y = function (itemName, itemProperty) {
    var itemsThatQualify = $(".oer-container, figure.embed.video");
    var total = itemsThatQualify.length;
    var haveProp = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "']").length;
    var yes = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
    var dontknow = total - haveProp;

    var level = (yes === 0 && no === 0 && total !== 0 ? "grey" : (yes === total || total === 0 ? "green" : (no === total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, yes, no, dontknow)
    };
  };
  
  /**
   * Check on "has-ebook"
   */
  afa.checkEbook = function (itemName, itemProperty) {
    // "has-ebook" only applies on oer container
    var total = 1;
    var yes = $(".oer-container meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = $(".oer-container meta[itemprop='" + itemProperty.name + "'][content='false']").length;

    var level = (yes === 0 && no === 0 && total !== 0 ? "grey" : (yes === total || total === 0 ? "green" : (no === total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, yes, no)
    };
  };
  
  /**
   * Check on "unknown" type
   * ToDo: This funciton is temporarily used for the AfA properties that the way to detect cannot be determined.
   * This function should be removed eventually.
   */
  afa.unknown = function (itemName, itemProperty) {
    return {
      level: "grey",
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], "grey")
    };
  };
  
  /**
   * Always return false state
   * ToDo: This funciton is temporarily used for the AfA properties that are assumed always return false.
   * This function should be removed eventually.
   */
  afa.alwaysFalse = function (itemName, itemProperty) {
    return {
      level: "red",
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], "red")
    };
  };
  
  // End of the functions that check on AfA properties
  
  afa.showMediaIcons = function (mediaSelector) {
      $(mediaSelector + " .afa-no-media").hide();
      $(mediaSelector + " .afa-media-icons").show();
  };

  /**
   * Loop thru all AfA items to check on grade.
   */
  afa.summerizeAfA = function () {
    var tooltipText, itemTagName;
    
    if ($(".oer-container img").length !== 0) {
        afa.showMediaIcons(".afa-images");
    }
    if ($(".oer-container figure.embed.video").length !== 0) {
        afa.showMediaIcons(".afa-video");
    }

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

  afa.addAfAToImage = function (img, hasAlt) {
      // TODO: These itemprop names should not be hard-coded
      img.wrap('<p itemscope />');
      if (hasAlt) {
        img.after('<meta itemprop="has-alt-text" content="true"/>');
      } else {
        img.after('<meta itemprop="has-alt-text" content="false"/>');
      }
      img.after('<meta itemprop="has-audio-representation" content="false"/>');
      img.after('<meta itemprop="has-long-description" content="false"/>');
  };

  afa.summerizeAfA();
})();

