var mymap = L.map('mapid').setView([51.505, -0.09], 13);
L.tileLayer('https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
	maxZoom: 18,
}).addTo(mymap);