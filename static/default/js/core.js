jQuery.noConflict();
jQuery.fn.log = function (msg) {
  try {
    console.log("%s: %o", msg, this);
    return this;
  } catch(e) {
    //alert(msg)
  }
  return this;
};

jQuery.fn.closemsg = function(options) {
  var settings = {"fadeout":1000, "delay":5000, "actionclose":".close"}
  if (options){
    jQuery.extend( settings, options );
  }
  this.each(function(){
    jQuery(this).delay(settings.delay)
           .fadeOut(settings.fadeout);
  })

  jQuery(settings.actionclose).click(function() {
    rel_id = '#' + jQuery(this).attr("rel");
    jQuery(rel_id).clearQueue().fadeOut(settings.fadeout);
    return false
  });
}

jQuery.fn.addHover = function(options) {
  var settings = {"textclass":"hover"}
  if (options) {
    jQuery.extend(settings, options)
  }
  return this.hover(
    function(){ jQuery(this).addClass(options.textclass); },
    function(){ jQuery(this).removeClass(options.textclass); }
  )
};