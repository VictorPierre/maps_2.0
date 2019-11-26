$( document ).ready(function() {
    //init Algolia search bars
    initAlgolia('plMDWCZD52QJ', 'b5cba8fb73a56e36a9a123facce6af93');

    //listen to updates
    placesAutocompleteDepart.on('change', function resultSelected(e) {
       document.querySelector('#start_lat').value = e.suggestion.latlng['lat'] || '';
       document.querySelector('#start_long').value = e.suggestion.latlng['lng'] || '';
    });
    placesAutocompleteArrivee.on('change', function resultSelected(e) {
       document.querySelector('#end_lat').value = e.suggestion.latlng['lat'] || '';
       document.querySelector('#end_long').value = e.suggestion.latlng['lng'] || '';
    });

    //init toggle button (Options)
    $(".toggleButton").on('click', function() {
        $("#options-content").toggle();
        $("#options>div").toggle();
    });

    //Overwrite form submission function
    $("#form").submit(function(e) {
        e.preventDefault(); // avoid to execute the actual submit of the form.
        var form = $(this);
        var url = form.attr('action');

        //group non owned vehicles in an array
        var forbidden_vehicles = [];
        $("input:not(:checked)[name='vehicles[]']").each(function(){forbidden_vehicles.push($(this).val());});
        $("#forbidden_vehicles").val(forbidden_vehicles)

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

//Variables initialisation
var placesAutocompleteDepart;
var placesAutocompleteArrivee;
var routes;
var map = L.map('mapid').setView([48.84, 2.34], 13);
tile = L.tileLayer('https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
	maxZoom: 18,
}).addTo(map);



var initAlgolia = function (appId,apiKey) {
    //Algolia search bar initialization
    var algolia_params = {
        appId: appId,
        apiKey: apiKey,
        aroundLatLng : "48.856496, 2.342510",
        aroundRadius : 7000,
        templates: {
            value: function(suggestion) {
                return suggestion.name +', '+suggestion.city;
            },
        }
    };

    placesAutocompleteDepart = places(
        Object.assign(
            {},
            algolia_params,
            {container: document.querySelector('#depart')}
        )
    );
    placesAutocompleteArrivee = places(
        Object.assign(
            {},
            algolia_params,
            {container: document.querySelector('#arrivee')}
        )
    );
}

var displayRoutes = function (routes) {
    $("#routes").empty()
    //display the distance & duration for all routes
    for (var i = 0; i < routes.length; i++) {
        //append the route
        $("#routes").append(routes[i]["html"])
        //create route id
        $("#routes .itinerary:last-child").attr('routeId', i)
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
    //Show markers
    showMarkers(routes[route_id].markers)
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

var showMarkers = function(markers){
    for (var i = 0; i < markers.length; i++) {
        if(markers[i].description==""){
            L.marker(markers[i].coordinates).addTo(map);
        }
        else{
            L.marker(markers[i].coordinates).addTo(map)
                .bindPopup(markers[i].description);
        }
    }
}

var resetMap = function () {
    map.eachLayer(function(layer){
        if(layer._leaflet_id!=tile["_leaflet_id"]){
            map.removeLayer(layer);
        }
    });
}
