STATIC_URL = window.STATIC_URL or "/media/"

SWF_URL = STATIC_URL + "javascripts/jquery/jme/player.swf"


class AudioPlayer

  constructor: (@figure)->
    @url = @figure.data("url")

    @player = @figure.find("div.audio-player")
    if not @player.length
      @player = $("""<div class="audio-player">
        <audio src="#{@url}"></audio>
        <div class="play-pause">play / pause</div>
        <div class="timeline-slider">
          <div class="progress"></div>
        </div>
      </div>""").prependTo(@figure)

    @player.jmeControl(
      embed:
        jwPlayer:
          path: SWF_URL
    )

    @progress = @player.find("div.progress")
    @player.find("audio").bind("timechange", (e, data)=>
      @progress.css(
        width: Math.floor(data.timeProgress) + "%"
      )
    )

    return


window.AudioPlayer = AudioPlayer
