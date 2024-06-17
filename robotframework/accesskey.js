var mapElement = document.querySelector('.leaflet-mapkit-mutant');
var dataMapPrintingBackground = mapElement.getAttribute('data-map-printing-background');
var accessKeyMatch = dataMapPrintingBackground.match(/accessKey=([^&]*)/);
