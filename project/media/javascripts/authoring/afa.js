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
      translations: {
          name: "has-translations ",
          type: "unknown",
          selector: ".translations",
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
      /* audio resource not yet supported, so these icons will not be used */
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
      captions: {
        name: "has-captions",
        type: "boolean",
        selector: ".captions",
        summaryfunc: "afa.unknown"  // ToDo: needs an actual summary function eventually
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
          no: "The display of some of the video players in this resource cannot be transformed.",
          dontknow: "It may not be possible to transform the presentation and interface of parts of this learning resource."
      },
      red: "It is not possible to transform the presentation and interface of this learning resource.",
      grey: "Cannot determine if this learning resource's presentation and interface can be transformed."
    },
    ebook: {
      heading: "eBook Export",
      green: "",
      yellow: "",
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
    translations: {
      heading: "Translations",
      grey: "Cannot determine if this learning resource is linked to any translations."
    },
    altText: {
      heading: "Alt Text",
      green: "All images in this learning resource have alternative text.",
      yellow: {
          no: "Some images in this learning resource have no alternative text.",
          dontknow: "It is possible that some images in this learning resource have no alternative text."
      },
      red: "No images in this learning resource have alternative text.",
      grey: "Cannot determine if the images in this learning resource have alternative text."
    },
    imgAudioAdapt: {
      heading: "Audio Adaptations",
      green: "",
      yellow: "",
      red: "No images in this learning resource are associated with audio descriptions.",
      grey: "Cannot determine if any images in this learning resource are associated with audio descriptions."
    },
    imgLongDesc: {
      heading: "Long Descriptions",
      green: "",
      yellow: {
          no: "Some images in this learning resource have no long descriptions.",
          dontknow: "It is possible that some images in this learning resource have no alternative text."
      },
      red: "No images in this learning resource are associated with long descriptions.",
      grey: "Cannot determine if the images in this learning resource have extended descriptions."
    },
    /* audio resource not yet supported, so these string will not be used */
    audioTrans: {
      heading: "Transcripts",
      green: "",
      yellow: "",
      red: "",
      grey: ""
    },
    audioVisualAdapt: {
      heading: "Visual Adaptations",
      green: "",
      yellow: "",
      red: "No videos in this learning resource have visual adaptations for the audio track.",
      grey: "Cannot determine if the audio tracks for videos in this learning resource have visual adaptations."
    },
    captions: {
      heading: "Translations",
      grey: "Cannot determine if the videos in this learning resource have captions."
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
      grey: "Cannot determine if the audio tracks for videos in this learning resource have visual adaptations."
    }
  };

  /**
   * Build an HTML string suitable for display in the tooltip. Currently, this builds a bulleted list.
   * @param lines   either a single string or an object containing three strings
   * @param no (optional) The number of resources negatively identified for this property
   * @param dontknow (optional) The number of resources undetermined for this property
   */
  afa.buildTooltipContent = function (strings, level, no, dontknow) {
      // TODO: This is entirely not configurable
      var string = "<h1>" + strings.heading + "</h1>";
      var lines = strings[level];
      if ((typeof lines) === 'string') {
          return string + "<ul><li>"+lines+"</li></ul>"
      }
      string += "<ul>";
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
    var $selector = $(".afa-summary "+selector);
    // remove the old level classes to have the new one in effect.
    $selector.removeClass("green yellow red grey");
    $selector.addClass(level);
  
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
    // only looks up on the visible images as the media upload dialog uses some images that are hidden.
    var $images = $(".oer-container img:visible");
    
    var total = $images.length;
    var yes = $images.parent().children("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = $images.parent().children("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
      
    var level = (yes === 0 && no === 0 && total !== 0 ? "grey" : (yes === total || total === 0 ? "green" : (no === total ? "red" : "yellow")));
    
    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, no)
    };
  };
  
  /**
   * Check on "display-transformable"
   * Currently, this is only present on the "body" and on videos
   * For now, this function treats the presence of any of the possible disp-trans values as "true"
   * and the absense (i.e. an empty string) as "false." Eventually, we should look at individual values
   */
  afa.checkDispTrans = function (itemName, itemProperty) {
    var itemsThatQualify = $(".oer-container, figure.embed.video");
    var total = itemsThatQualify.length;
    var haveProp = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "']").length;
    var yes = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='true']").length;
    var no = itemsThatQualify.find("meta[itemprop='" + itemProperty.name + "'][content='false']").length;
    var dontknow = total - haveProp;

    var level = (yes === 0 && no === 0 && total !== 0 ? "grey" : (yes === total || total === 0 ? "green" : (no === total ? "red" : "yellow")));

    return {
      level: level,
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, no, dontknow)
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
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, no, dontknow)
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
      tooltipText: afa.buildTooltipContent(tooltipTextMapping[itemName], level, no)
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
  
  afa.updateMediaIconDisplay = function (mediaSelector, show) {
      $(mediaSelector + " .afa-no-media").toggle(!show);
      $(mediaSelector + " .afa-media-icons").toggle(show);
  }

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

    afa.updateMediaIconDisplay(".afa-images", $(".oer-container img:visible").length !== 0);
    afa.updateMediaIconDisplay(".afa-video", $(".oer-container figure.embed.video").length !== 0);
  };
  
  afa.addAfAToBody = function () {
    var container = $(".oer-container");
    container.attr("itemscope", "");

    // TODO: These itemprop strings should not be hard-coded
    container.prepend('<meta itemprop="is-mouse-accessible" content="true"/>');
    container.prepend('<meta itemprop="is-keyboard-accessible" content="true"/>');
    // TODO: The value of "is-display-transformable" should be a list of relevant strings, but in
    // this iteration, we're treating it as a boolean
    container.prepend('<meta itemprop="is-display-transformable" content="true"/>');
    container.prepend('<meta itemprop="has-ebook" content="false"/>');
    container.prepend('<meta itemprop="hazard" content=""/>');
  }
  
  afa.addAfAToEmbeddedVideo = function (figure) {
      // NOTE: These values are valid for currently-supported embedded youtube videos only
      // TODO: These itemprop names should not be hard-coded
      figure.attr("itemscope", "");
      figure.prepend('<meta itemprop="is-mouse-accessible" content="true"/>');
      figure.prepend('<meta itemprop="has-transcript" content="false"/>');
    // TODO: The value of "is-display-transformable" should be an empty string for something that is
    // known to be non-tranformable, but in this iteration, we're treating it as a boolean
      figure.prepend('<meta itemprop="is-display-transformable" content="false"/>');
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

