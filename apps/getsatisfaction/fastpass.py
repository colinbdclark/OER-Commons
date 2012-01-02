import oauth
import cgi

class FastPass:
  domain = "getsatisfaction.com"
  
  @staticmethod
  def url(key, secret, email, name, uid, isSecure=False, **additionalFields):
    consumer = oauth.OAuthConsumer(key, secret)
    url = "http://%s/fastpass" % FastPass.domain
    if isSecure:
      url = "https://%s/fastpass" % FastPass.domain
    params = dict(email = email, name = name, uid = uid)
    params.update(additionalFields)
    sigmethod = oauth.OAuthSignatureMethod_HMAC_SHA1()
    request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url = url, parameters = params)
    request.sign_request(sigmethod, consumer, None)
    return request.to_url()
    
  @staticmethod
  def image(key, secret, email, name, uid, isSecure=False, **additionalFields):
    return "<img src=\"%s\" alt="" />" % cgi.escape(FastPass.url(key, secret, email, name, uid, isSecure, **additionalFields))
    
  @staticmethod
  def script(key, secret, email, name, uid, isSecure=False, **additionalFields):
    url = FastPass.url(key, secret, email, name, uid, isSecure, **additionalFields)
    return """
    <script type="text/javascript">
      var GSFN;
      if(GSFN == undefined) { GSFN = {}; }
      
      (function(){
        add_js = function(jsid, url) {
          var head = document.getElementsByTagName("head")[0];
          script = document.createElement('script');
          script.id = jsid;
          script.type = 'text/javascript';
          script.src = url;
          head.appendChild(script);
        }

        add_js("fastpass_common", document.location.protocol + "//getsatisfaction.com/javascripts/fastpass.js");

        if(window.onload) { var old_load = window.onload; }
        window.onload = function() {
          if(old_load) old_load();
          add_js("fastpass", "%s");
        }
      })()

    </script>
    """ % (url)


# print FastPass.script(
#   "xi2vaxgpp06m", 
#   "ly68der0hk8idfr5c73ozyq56jpwstd1", 
#   "scott@getsatisfaction.com", 
#   "Scott", 
#   "nullstyle",
#   False,
#   foo = "bar")