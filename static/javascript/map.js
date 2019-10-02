
var map = L.map('mapid').setView([48.84, 2.34], 13);
L.tileLayer('https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
	maxZoom: 18,
}).addTo(map);

var myStyle = {
	"color": "#ff7800",
	"weight": 5,
	"opacity": 0.65
};

L.geoJSON(geojsonFeature, {
	style: myStyle
}).addTo(map);