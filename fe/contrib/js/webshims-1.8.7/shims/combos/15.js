jQuery.webshims.register("details",function(a,k,i,l,c,h){var n=function(b){var d=a(b).parent("details");if(d[0]&&d.children(":first").get(0)===b)return d},e=function(b,d){var b=a(b),d=a(d),f=a.data(d[0],"summaryElement");a.data(b[0],"detailsElement",d);if(!f||b[0]!==f[0])f&&(f.hasClass("fallback-summary")?f.remove():f.unbind(".summaryPolyfill").removeData("detailsElement").removeAttr("role").removeAttr("tabindex").removeAttr("aria-expanded").removeClass("summary-button").find("span.details-open-indicator").remove()),
a.data(d[0],"summaryElement",b),d.prop("open",d.prop("open"))};k.createElement("summary",function(){var b=n(this);if(b&&!a.data(this,"detailsElement")){var d;e(this,b);a(this).bind("focus.summaryPolyfill",function(){a(this).addClass("summary-has-focus")}).bind("blur.summaryPolyfill",function(){a(this).removeClass("summary-has-focus")}).bind("mouseenter.summaryPolyfill",function(){a(this).addClass("summary-has-hover")}).bind("mouseleave.summaryPolyfill",function(){a(this).removeClass("summary-has-hover")}).bind("click.summaryPolyfill",
function(a){var b=n(this);b&&(clearTimeout(d),d=setTimeout(function(){a.isDefaultPrevented()||b.prop("open",!b.prop("open"))},0))}).bind("keydown.summaryPolyfill",function(b){if((13==b.keyCode||32==b.keyCode)&&!b.isDefaultPrevented())b.preventDefault(),a(this).trigger("click")}).attr({tabindex:"0",role:"button"}).prepend('<span class="details-open-indicator" />')}});var g;k.defineNodeNamesBooleanProperty("details","open",function(b){var d=a(a.data(this,"summaryElement"));if(d){var c=b?"removeClass":
"addClass",e=a(this);if(!g&&h.animate){e.stop().css({width:"",height:""});var j={width:e.width(),height:e.height()}}d.attr("aria-expanded",""+b);e[c]("closed-details-summary").children().not(d[0])[c]("closed-details-child");!g&&h.animate&&(b={width:e.width(),height:e.height()},e.css(j).animate(b,{complete:function(){a(this).css({width:"",height:""})}}))}});k.createElement("details",function(){g=!0;var b=a.data(this,"summaryElement");b||(b=a("> summary:first-child",this),b[0]?e(b,this):(a(this).prependPolyfill('<summary class="fallback-summary">'+
h.text+"</summary>"),a.data(this,"summaryElement")));a.prop(this,"open",a.prop(this,"open"));g=!1})});
(function(a){if(!navigator.geolocation){var k=function(){setTimeout(function(){throw"document.write is overwritten by geolocation shim. This method is incompatible with this plugin";},1)},i=0,l=a.webshims.cfg.geolocation.options||{};navigator.geolocation=function(){var c,h={getCurrentPosition:function(h,e,g){var b=2,d,f,i,j=function(){if(!i)if(c){if(i=!0,h(a.extend({timestamp:(new Date).getTime()},c)),m(),window.JSON&&window.sessionStorage)try{sessionStorage.setItem("storedGeolocationData654321",
JSON.stringify(c))}catch(d){}}else e&&!b&&(i=!0,m(),e({code:2,message:"POSITION_UNAVAILABLE"}))},p=function(){b--;o();j()},m=function(){a(document).unbind("google-loader",m);clearTimeout(f);clearTimeout(d)},o=function(){if(c||!window.google||!google.loader||!google.loader.ClientLocation)return!1;var b=google.loader.ClientLocation;c={coords:{latitude:b.latitude,longitude:b.longitude,altitude:null,accuracy:43E3,altitudeAccuracy:null,heading:parseInt("NaN",10),velocity:null},address:a.extend({streetNumber:"",
street:"",premises:"",county:"",postalCode:""},b.address)};return!0};if(!c&&(o(),!c&&window.JSON&&window.sessionStorage))try{c=(c=sessionStorage.getItem("storedGeolocationData654321"))?JSON.parse(c):!1,c.coords||(c=!1)}catch(q){c=!1}c?setTimeout(j,1):l.confirmText&&!confirm(l.confirmText.replace("{location}",location.hostname))?e&&e({code:1,message:"PERMISSION_DENIED"}):(a.ajax({url:"http://freegeoip.net/json/",dataType:"jsonp",cache:!0,jsonp:"callback",success:function(a){b--;a&&(c=c||{coords:{latitude:a.latitude,
longitude:a.longitude,altitude:null,accuracy:43E3,altitudeAccuracy:null,heading:parseInt("NaN",10),velocity:null},address:{city:a.city,country:a.country_name,countryCode:a.country_code,county:"",postalCode:a.zipcode,premises:"",region:a.region_name,street:"",streetNumber:""}},j())},error:function(){b--;j()}}),clearTimeout(f),!window.google||!window.google.loader?f=setTimeout(function(){if(l.destroyWrite)document.write=k,document.writeln=k;a(document).one("google-loader",p);a.webshims.loader.loadScript("http://www.google.com/jsapi",
!1,"google-loader")},800):b--,d=g&&g.timeout?setTimeout(function(){m();e&&e({code:3,message:"TIMEOUT"})},g.timeout):setTimeout(function(){b=0;j()},1E4))},clearWatch:a.noop};h.watchPosition=function(a,c,g){h.getCurrentPosition(a,c,g);i++;return i};return h}();a.webshims.isReady("geolocation",!0)}})(jQuery);