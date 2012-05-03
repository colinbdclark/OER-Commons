(function() {
  var AudioPlayer, STATIC_URL, SWF_URL;

  STATIC_URL = window.STATIC_URL || "/media/";

  SWF_URL = STATIC_URL + "javascripts/jquery/jme/player.swf";

  AudioPlayer = (function() {

    function AudioPlayer(figure) {
      var _this = this;
      this.figure = figure;
      this.url = this.figure.data("url");
      this.player = this.figure.find("div.audio-player");
      if (!this.player.length) {
        this.player = $("<div class=\"audio-player\">\n  <audio src=\"" + this.url + "\"></audio>\n  <div class=\"play-pause\">play / pause</div>\n  <div class=\"timeline-slider\">\n    <div class=\"progress\"></div>\n  </div>\n</div>").prependTo(this.figure);
      }
      this.player.jmeControl({
        embed: {
          jwPlayer: {
            path: SWF_URL
          }
        }
      });
      this.progress = this.player.find("div.progress");
      this.player.find("audio").bind("timechange", function(e, data) {
        return _this.progress.css({
          width: Math.floor(data.timeProgress) + "%"
        });
      });
      return;
    }

    return AudioPlayer;

  })();

  window.AudioPlayer = AudioPlayer;

}).call(this);
