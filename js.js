// Google Analytics
var _gaq = _gaq || [];_gaq.push(['_setAccount', 'UA-28191910-1']);_gaq.push(['_trackPageview']); (function() {var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);})();

$(function() {
	colors = new Array("#A200FF","#FF0097","#00ABA9","#8CBF26","#E671B8","#ORANGE","#F09609","#1BA1E2","#339933");
	$("body").css("background-color",colors[Math.round(Math.random()*colors.length)]);
	
	$("#faculteit").change(function() {
		
		window.location.href = "index.py?faculty=" + $(this).val()
		
	});
	$("form").live("submit", function() {
		$("form input[type=submit]").prop("disabled", true);
		$("form input[type=submit]").attr("value","Loading...");
		
		setTimeout(function() {
			$("#slider").animate({"margin-left":"-120%",opacity:"0"},800);
		}, 500);
		
		setTimeout(function() {
			$("#slider").css({"margin-left":"120%"});
			$("form input[type=submit]").prop("disabled", false);
			$("form input[type=submit]").attr("value","Download");
			$("form").css("display","none");
			$("#success").css("display","block");
			$("#help").css("display","none");
		},1500);
		
		if( $("input#ics").is(':checked') ) { 
			$("#webcal_block").css("display","block");
			webcalLink = "webcal://cytosine.nl/~stephan/RoosterLoader/index.py/cache?g=" + $("#groep").val() + "&faculty=" + $("#faculteit").val()
			$("#webcal_link").val(webcalLink)
		} else if( $("input#icsnz").is(':checked') ) { 
			$("#webcal_block").css("display","block");
			webcalLink = "webcal://cytosine.nl/~stephan/RoosterLoader/index.py/cache?nz=1&g=" + $("#groep").val() + "&faculty=" + $("#faculteit").val()
			$("#webcal_link").val(webcalLink)
		} else {
			$("#webcal_block").css("display","none");
		}
		
		setTimeout(function() {
			$("#slider").animate({"margin":"0",opacity:"1"},800);
			$(".back_button").animate({opacity:"1"});			
		}, 2000);
		
	});
	
	$("#copy_webcal_button").live("mouseenter", function() {
		$("#copy_webcal_button").zclip({
			path:'ZeroClipboard.swf',
			copy: function(){ return $('#webcal_link').val(); },
			afterCopy:function(){
				$('#webcal_link').val("Gekopieërd!")
				$('#webcal_block').fadeOut(1000)				
			}
		});	
	});
	
	$(".revert").live("click", function() {
		$(".back_button").animate({opacity:"0"});
		$("#slider").animate({"margin-left":"120%",opacity:"0"},800);
		
		setTimeout(function() {
			$("#slider").css({"margin-left":"-120%"});
			$("form").css("display","block");
			$("#success, #disclaimer").css("display","none");
			$("#help").css("display","none");
		},1000);
		
		setTimeout(function() {
			$("#slider").animate({"margin":"0",opacity:"1"},800);
		}, 1100);
	});
	
	$(".to_help").live("click", function() {
		$("#slider").animate({"margin-left":"-120%",opacity:"0"},800);
		
		setTimeout(function() {
			$("#slider").css({"margin-left":"120%"});
			$("form").css("display","none");
			$("#success, #disclaimer").css("display","none");
			$("#help").css("display","block");
			
		},1000);
		
		setTimeout(function() {
			$("#slider").animate({"margin":"0",opacity:"1"},800);
			$(".back_button").animate({opacity:"1"});
		}, 1100);
	});
	
	$(".to_disclaimer").live("click", function() {
		$("#slider").animate({"margin-left":"-120%",opacity:"0"},800);
		
		setTimeout(function() {
			$("#slider").css({"margin-left":"120%"});
			$("form").css("display","none");
			$("#success").css("display","none");
			$("#disclaimer").css("display","block");
			
		},1000);
		
		setTimeout(function() {
			$("#slider").animate({"margin":"0",opacity:"1"},800);
			$(".back_button").animate({opacity:"1"});
		}, 1100);
	});
	
});
