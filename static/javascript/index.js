$( document ).ready(function() {
    var algolia_params = {
        appId: 'plMDWCZD52QJ',
        apiKey: 'b5cba8fb73a56e36a9a123facce6af93',
        aroundLatLng : "48.857832, 2.346579",
        aroundRadius : 40000,
    }
    var placesAutocompleteDepart = places({
        appId: 'plMDWCZD52QJ',
        apiKey: 'b5cba8fb73a56e36a9a123facce6af93',
        aroundLatLng : "48.857832, 2.346579",
        aroundRadius : 40000,
        container: document.querySelector('#depart')
    });

    var placesAutocompleteArrivee = places({
        appId: 'plMDWCZD52QJ',
        apiKey: 'b5cba8fb73a56e36a9a123facce6af93',
        aroundLatLng : "48.857832, 2.346579",
        aroundRadius : 40000,
        container: document.querySelector('#arrivee')
    });
    placesAutocompleteDepart.on('change', function resultSelected(e) {
       document.querySelector('#start_lat').value = e.suggestion.latlng['lat'] || '';
       document.querySelector('#start_long').value = e.suggestion.latlng['lng'] || '';
    });

    placesAutocompleteArrivee.on('change', function resultSelected(e) {
       document.querySelector('#end_lat').value = e.suggestion.latlng['lat'] || '';
       document.querySelector('#end_long').value = e.suggestion.latlng['lng'] || '';
    });

    //Form submission
    $("#form").submit(function(e) {
        e.preventDefault(); // avoid to execute the actual submit of the form.
        var form = $(this);
        var url = form.attr('action');
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
            success : function(response, status){
                routes = response
                displayRoutes(routes)
            },
            error : function(response, status, error){
                $("#routes").html(response)
            }
        });
    });
});

var routes;

//Map initialisation
var map = L.map('mapid').setView([48.84, 2.34], 13);
tile = L.tileLayer('https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
	maxZoom: 18,
}).addTo(map);


var displayRoutes = function (routes) {
    $("#routes").empty()
    //display the distance & duration for all routes
    for (var i = 0; i < routes.length; i++) {
        //append the route
        $("#routes").append(routes[i]["html"])
        //create route id
        $("#routes .itinerary:last-child").attr('routeId', i)
    }
    //show the appropriate rain message
    if (rain){
        $(".rain-ok").hide()
        $(".rain-alert").show()
    }

    highlightRoute(0);
    $(".itinerary").on('click', function(){
        routeId = parseInt($(this).attr("routeId"));
        highlightRoute(routeId)
    })
}

var highlightRoute = function(route_id){
    //Show the geojson of the route
    showGeoJSON(routes[route_id]["geojson"])
    //Add the highlighted attribute to the div
    $("#routes .itinerary").removeAttr('highlighted')
    $("#routes .itinerary:nth-child("+(route_id+1)+")").attr('highlighted', '')

}

var showGeoJSON = function(geojson){
    //Reset the map
    resetMap();
    //display the geojson
    markersLayer = L.geoJSON(geojson, {
        style: function(feature) {
            return {
                "color": feature.properties.color || "#000000",
                "weight": 5,
                "opacity": 1
            };
        }
    }).addTo(map);
    map.fitBounds(markersLayer.getBounds());
}

var resetMap = function () {
    map.eachLayer(function(layer){
        if(layer._leaflet_id!=tile["_leaflet_id"]){
            map.removeLayer(layer);
        }
    });
}
