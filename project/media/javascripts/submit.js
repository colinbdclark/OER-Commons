XD = function() {

    var interval_id, last_hash, cache_bust = 1, attached_callback, window = this;

    return {
    postMessage : function(message, target_url, target) {
        if (!target_url) {
            return;
        }
        target = target || parent; // default to parent
        if (window['postMessage']) {
            // the browser supports window.postMessage, so call it with a
            // targetOrigin
            // set appropriately, based on the target_url parameter.
            target['postMessage'](message, target_url.replace(/([^:]+:\/\/[^\/]+).*/, '$1'));
        } else if (target_url) {
            // the browser does not support window.postMessage, so use the
            // window.location.hash fragment hack
            target.location = target_url.replace(/#.*$/, '') + '#' + (+new Date) + (cache_bust++) + '&' + message;
        }
    },
    receiveMessage : function(callback, source_origin) {
        // browser supports window.postMessage
        if (window['postMessage']) {
            // bind the callback to the actual event associated with
            // window.postMessage
            if (callback) {
                attached_callback = function(e) {
                    if ((typeof source_origin === 'string' && e.origin !== source_origin) || (Object.prototype.toString.call(source_origin) === "[object Function]" && source_origin(e.origin) === !1)) {
                        return !1;
                    }
                    callback(e);
                };
            }
            if (window['addEventListener']) {
                window[callback ? 'addEventListener' : 'removeEventListener']('message', attached_callback, !1);
            } else {
                window[callback ? 'attachEvent' : 'detachEvent']('onmessage', attached_callback);
            }
        } else {
            // a polling loop is started & callback is called whenever the
            // location.hash changes
            interval_id && clearInterval(interval_id);
            interval_id = null;
            if (callback) {
                interval_id = setInterval(function() {
                    var hash = document.location.hash, re = /^#?\d+&/;
                    if (hash !== last_hash && re.test(hash)) {
                        last_hash = hash;
                        callback({
                            data : hash.replace(re, '')
                        });
                    }
                }, 100);
            }
        }
    }
    };
}();

XD.receiveMessage(function(message) {
    if (message.data === "close") {
        var iframe = document.getElementById("oer-submit");
        iframe.parentNode.removeChild(iframe);
    }
}, OER_HOST);

var OER = {};

OER.showForm = function() {
    var body = document.getElementsByTagName("body")[0];
    var iframe = document.createElement("iframe");
    iframe.src = OER_HOST + "/submit?url=" + document.location.href + "#" + encodeURIComponent(document.location.href);
    iframe.style.position = "fixed";
    iframe.style.top = "10px";
    iframe.style.right = "10px";
    iframe.style["border-width"] = "5px";
    iframe.style["border-style"] = "solid";
    iframe.style["border-color"] = "#ccc";
    iframe.style["z-index"] = "9999";
    iframe.style["background-color"] = "#fff";
    iframe.width = 650;
    iframe.height = 550;
    iframe.id = "oer-submit";
    body.appendChild(iframe);
}

OER.showForm();
