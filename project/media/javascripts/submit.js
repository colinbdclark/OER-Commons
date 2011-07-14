var OER = {};

OER.showForm = function() {
    if (document.location.href.search(/^http/) == -1) {
        return;
    }

    var body = document.getElementsByTagName("body")[0];

    var container1 = document.createElement("div");
    container1.style.position = "absolute";
    container1.style.top = "0px";
    container1.style.right = "0px";
    container1.style.margin = "10px";
    container1.style.position = "absolute";
    container1.style.zIndex = "100000";

    body.appendChild(container1);

    var container2 = document.createElement("div");
    container2.style.borderWidth = "5px";
    container2.style.borderStyle = "solid";
    container2.style.borderColor = "#ccc";
    container2.style.position = "fixed";
    container2.style.backgroundColor = "#ffffff";
    container2.style.zIndex = "2";
    container2.style.top = "10px";
    container2.style.right = "10px";
    container2.style.width = "650px";
    container2.style.height = "470px";
    container2.style.overflow = "hidden";

    container1.appendChild(container2);

    var iframe = document.createElement("iframe");
    var load_counter = 0;
    iframe.src = OER_HOST + "/submit?url=" + encodeURIComponent(document.location.href);
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.border = "0px";
    iframe.id = "oer-submit";
    iframe.onload = function() {
      if (load_counter > 2) {
          container1.parentNode.removeChild(container1);
          load_counter = 0;
      }
      load_counter++;
    };

    container2.appendChild(iframe);
    
}

OER.showForm();
