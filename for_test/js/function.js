<!--
//floating

/*
$(document).ready(function () {  
  
    $(window).scroll(function (event) {
      // what the y position of the scroll is
      var y = $(this).scrollTop()-0;
		      
      $('#mast-float').css('margin-top',y+'px');
    });
});
*/

//fancy box
$(document).ready(function() {

			$("a[rel=works]").fancybox({
				'titlePosition'		: 'outside',
				'overlayColor'		: '#000',
				'overlayOpacity'	: 0.9
			});
		});
		
//open in new window
/*
var $j = jQuery.noConflict(); 
$j(document).ready(
	function() { 
	//external attribute
		$j('a:not([@href*=http://YOURSITE.com/])').not("[href^=#]")
		.addClass("external")
		.attr({ target: "_blank" }); 
	}
);
*/
$(document).ready(function() {
  $('a[rel="external"]').click(function(){
    $(this).attr('target','_blank');
  });
});

//toggle div

function toggle(id) {
	$("#"+id).toggle(300);
};

//go back
function goback()
{
	history.go(-1);
}	
//clear input
function clearDefaultText (el,message)
{
	var obj = el;
	if(typeof(el) == "string")
	obj = document.getElementById(id);
	if(obj.value == message)
	{
	obj.value = "";
	}
	obj.onblur = function()
	{
		if(obj.value == "")
		{
		obj.value = message;
		}
	}
}

//google map
/*
list=new Array();
urls=new Array();
names=new Array();

function getHL(str,n,url){
	 list.push(str);
	 urls.push(url);
	 names.push(n);
}
function initialize(){
	if(list.length>0){
		init();
	}else{
		document.getElementById('map_canvas').style.display="none";
	}
}
*/
// -->