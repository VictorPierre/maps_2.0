
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



    });


