(function( $ ) {


  jQuery.fn.magicForm = function(options) {

    var ignore = ['submit', 'hidden'];
    var inputs = this.find(':input');
    var self = this;
    this.attr('onsubmit','return false;')

    var settings = $.extend( {
      'url': '/',
      'type'         : 'POST',
    }, options);

    this.submitForm = function(){
      //make sure the data is the as new as possible before submission
      if(settings.loading != null){
        settings.loading(settings.loadingOptions);
      }
      console
      settings.data = self.serialize();
    	$.ajax(settings);
    };

    //bind all the relevant 
    this.bind = function(){
     $.each(inputs,function(i, each){
      	if($.inArray($(each).attr('type'),ignore) == -1){
      		$(each).keypress(function(e){
      			if(e.keyCode == 13){
      				self.submitForm();
      			}
      		});
      	}
        if($(each).attr('type') == 'submit'){
          $(each).on('click',self.submitForm);
        }
      });
    }
    this.bind();
    return this;
  };

})( jQuery );
