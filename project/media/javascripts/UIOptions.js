/*global jQuery, fluid*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */


(function ($) {
    $(document).ready(function () {
        var static_url = $(".flc-uiOptions").find(":hidden[name='static_url']").val();
        
        fluid.pageEnhancer({
            tocTemplate: static_url + "javascripts/infusion/components/tableOfContents/html/TableOfContents.html"
        });

        fluid.uiOptions.fatPanel.withMediaPanel(".flc-uiOptions", {
            prefix: static_url + "javascripts/infusion/components/uiOptions/html/",
            slidingPanel: {
                options: {
                    strings: {
                        showText: "+ Learner Options",
                        hideText: "- Learner Options"
                    }
                }
            },
            components: {
                relay: {
                    type: "fluid.videoPlayer.relay"
                },
                templateLoader: {
                    options: {
                        templates: {
                            mediaControls: static_url + "javascripts/videoPlayer/html/UIOptionsTemplate-media.html"
                        }
                    }
                }
            }
        });
        
    });
    
})(jQuery);
