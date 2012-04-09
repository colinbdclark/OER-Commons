/*
Copyright 2012 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

/*global jQuery, window, fluid*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

(function ($) {

    fluid.defaults("fluid.subtitleWidget", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        preInitFunction: "fluid.subtitleWidget.preInit",
        postInitFunction: "fluid.subtitleWidget.postInit",
        model: {
            languages: []
        },
        events: {
            onReady: null,
            onUnisub: null,
            onFetcher: null,
            createPanel: {
                events: {
                    unisub: "{fluid.subtitleWidget}.events.onUnisub",
                    fetcher: "{fluid.subtitleWidget}.events.onFetcher"
                }
            },
            modelReady: null
        },
        listeners: {
            createPanel: {
                listener: "{fluid.subtitleWidget}.createPanelHandler",
                priority: "last"
            }
        },
        styles: {
            mainWrap: "fl-subtitle-mainWrap",
            videoWrap: "fl-subtitle-videoWrap",
            widgetWrap: "fl-subtitle-widgetWrap"
        },
        url: "",
        getUrl: "fluid.subtitleWidget.getUrl",
        components: {
            unisub: {
                type: "fluid.unisubComponent",
                options: {
                    urls: {
                        video: "{subtitleWidget}.options.url"
                    },
                    model: "{subtitleWidget}.model",
                    applier: "{subtitleWidget}.applier",
                    events: {
                        onReady: "{fluid.subtitleWidget}.events.onUnisub",
                        modelReady: "{fluid.subtitleWidget}.events.modelReady"
                    }
                }
            },
            resourceFetcher: {
                type: "fluid.resourceFetcher",
                options: {
                    resourceTemplate: "{fluid.subtitleWidget}.options.templateUrl",
                    containerBody: "{fluid.subtitleWidget}.options.widgetWrap",
                    events: {
                        onReady: "{fluid.subtitleWidget}.events.onFetcher"
                    }
                }
            },
            widget: {
                type: "fluid.subtitlePanel",
                createOnEvent: "createPanel",
                container: "{subtitleWidget}.options.widgetWrap",
                options: {
                    videoLink: "{subtitleWidget}.options.url",
                    resources: "{resourceFetcher}.options.resources",
                    model: "{subtitleWidget}.model"
                }
            }
        },
        templateUrl: "../html/SubtitlePanel_template.html",
        mainWrap: null,
        widgetWrap: null,
        videoWrap: null
    });

    fluid.subtitleWidget.preInit = function (that) {
        that.createPanelHandler = function () {
            that.events.onReady.fire(that);
        };
    };

    fluid.subtitleWidget.getUrl = function (that) {
        return that.container.data("url");
    }; 
    
    fluid.subtitleWidget.postInit = function (that) {

        if (!that.options.url) {
            var getUrl = that.options.getUrl;
            that.options.url = typeof getUrl === "string" ? fluid.invokeGlobalFunction(getUrl, [that]) : getUrl(that);
        }

        var styles = that.options.styles;
        var container = that.container;
        
        // First create a markup for the video where we want to attach our widget
        var mainWrap = $("<div />").addClass(styles.mainWrap);
        var widgetWrap = $("<div />").addClass(styles.widgetWrap);
        var videoWrap = $("<div/>").addClass(styles.videoWrap);
        
        mainWrap.append(widgetWrap);
        mainWrap.append(videoWrap);
                
        mainWrap.insertBefore(container);
                
        container.appendTo(videoWrap);
        
        that.options.mainWrap = mainWrap;
        that.options.widgetWrap = widgetWrap;
        that.options.videoWrap = videoWrap;
    };


})(jQuery);