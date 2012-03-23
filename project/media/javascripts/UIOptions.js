/*

Copyright 2012 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

/*global jQuery, fluid*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */


(function ($) {
    $(document).ready(function () {
        var static_url = $(".flc-uiOptions").find(":hidden[name='static_url']").val();
        
        fluid.pageEnhancer({
            tocTemplate: static_url + "javascripts/infusion/components/tableOfContents/html/TableOfContents.html"
        });

        fluid.uiOptions.fatPanel(".flc-uiOptions", {
            prefix: static_url + "javascripts/infusion/components/uiOptions/html/"
        });
        
    });
    
})(jQuery);
