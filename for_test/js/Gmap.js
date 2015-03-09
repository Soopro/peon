<!--
 
    var map = null;
    var geocoder = null;
	
    function init() {
      if (GBrowserIsCompatible()) {
        map = new GMap2(document.getElementById("map_canvas"));
        geocoder = new GClientGeocoder();
        bounds = new GLatLngBounds();
        listLength = list.length;
	    i = 0;
		
        var baseIcon = new GIcon();
		baseIcon.image = "images/marker.png";
        baseIcon.shadow = "images/shadow50.png";
        baseIcon.iconSize = new GSize(20, 34);
        baseIcon.shadowSize = new GSize(37, 34);
        baseIcon.iconAnchor = new GPoint(16, 16);
        baseIcon.infoWindowAnchor = new GPoint(16, 2);
        baseIcon.infoShadowAnchor = new GPoint(16, 25);
        
        markerOptions = { icon:baseIcon };
        map.addControl(new GLargeMapControl());
       /* var customUI = map.getDefaultUI();
        customUI.maptypes.satellite = false;
        customUI.maptypes.physical = false;
		customUI.maptypes.hybrid = false;
        
        map.setUI(customUI);*/
		
		map.disableScrollWheelZoom();
		
		loop();
      }
    }
	
	function loop ()
	{
		showAddress(list[i],names[i],urls[i]);
		/*alert(names[i]);*/
		i = i + 1;
		if (i < listLength)
		{
			window.setTimeout("loop()", 500);
		}
	}
 
    function showAddress(address,name,url) 
    {
      if (geocoder) 
      {
        geocoder.getLatLng(
          address,
          function(point) 
          {
            if (!point) 
            {
              //alert("Error: " + address);
            } 
            else 
            {
              var marker = new GMarker(point,markerOptions);
              bounds.extend(point);
			  if (map.getBoundsZoomLevel(bounds) > 15)
			  {
				  var zoomlevel = 15;
			  }
			  else
			  {
			  	 var zoomlevel = map.getBoundsZoomLevel(bounds)-1;
			  }
              map.setCenter(bounds.getCenter(),zoomlevel);
              map.addOverlay(marker);
              GEvent.addListener(marker,"click",
              	function() 
              	{
              		var myHtml = "<span style='display:block;padding-top:20px;font-width:700;'><strong>" + name + "</strong><br />" + address + "</span>";
              		/* var myHtml = "<a href=" + url + " style='display:block;padding-top:20px;font-width:700;'>" + name + "</a>"; */
              		map.openInfoWindowHtml(point,myHtml);
              	}
              );            
            }
          }
        );
      }
    }
// -->