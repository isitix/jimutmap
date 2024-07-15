async function getAccessKey(page) {
  const mapElement = await page.$('.leaflet-mapkit-mutant');
  var dataMapPrintingBackground = mapElement.getAttribute('data-map-printing-background');
  return dataMapPrintingBackground;
}

exports.__esModule = true;
exports.getAccessKey = getAccessKey;