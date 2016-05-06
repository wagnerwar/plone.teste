(function($) {

$(document).ready(function(){
	$(window).load(function(){
            var tempo = 5000;
            var index = 1;
       	    function exibeAnuncios(){
              $('div.anuncio-inativo').each(function(i,v){
                ind=i+1;
                console.log("INDICE DE ENTRADA: " + ind);

                if(ind == index){
                    console.log("Indice sendo considerado: " + ind);
                   $(".anuncio-ativo").removeClass("anuncio-ativo");
                   $(this).addClass("anuncio-ativo");
		}
              });
	    } 
            var timer = setInterval(function(){
              console.log("INDEQS: " + index);
              exibeAnuncios();
              //tempo = tempo*index;
              index++;
              if($("div.anuncio-inativo").length < index){
                 index = 1;
              }
            }, tempo);
	});
});

})(jQuery);

