$('#logout-button').click(function(){
    window.location = '/logout';
});

$('#add-fav-location').click(function(){
    // var location_id = $('#add-fav-location').siblings()[0].value;
    var location_id = $('#select-location').val();
    // var location_name = $('#select-location option:selected').data('name');
    // $('#locations-list').append(location_name);
    $.post(
        '/new-location', 
        {location_id: location_id}, 
        function(results){
            var newMarkerLayer = L.mapbox.featureLayer();
            newMarkerLayer.on('layeradd', addMarkers);
            layerGroup.addLayer(newMarkerLayer);
            newMarkerLayer.setGeoJSON(results.marker_collection);
            var newLocation = $('<p>').html(results.location_name);
            $('#locations-list').append(newLocation);
    });
});


// per Mapbox mentors, it's okay that this key is not secret
L.mapbox.accessToken = 'pk.eyJ1Ijoiam1sYW5nc3RvbiIsImEiOiI1MGFhMGUzZmFjOTJjMmFkYTVjZTQ0MDExYjQ4NzhkYyJ9.xjCipe1mRK_lbjkQruXkvA';

// Instantiate map.  First arg is the html element id ('map').
// Second arg is the specific map. Right now is a default mapbox.streets map. Later can replace this with map I design in Mapbox Studio.
var map = L.mapbox.map('map', 'jmlangston.f9c7d38b', {
    scrollWheelZoom: false
    }).setView([20, 0], 2);


var popupsLayer = L.mapbox.featureLayer();

var layerGroup = L.layerGroup().addLayer(popupsLayer).addTo(map);

popupsLayer.on('layeradd', addMarkers);

// popupsLayer.setGeoJSON({{ marker_collection | safe }});
popupsLayer.setGeoJSON(markerCollection);

function addMarkers(evt) {
    var marker = evt.layer;
    var feature = marker.feature;

    var popupContent = '<h1 class="popup-header">' + feature.properties.title + '</h1><div class="popup-articles"><p><a href="' + feature.properties.article_1_url + '">' + feature.properties.article_1_headline + '</a><br>' + feature.properties.article_1_date + '</p><p><a href="' + feature.properties.article_2_url + '">' + feature.properties.article_2_headline + '</a><br>' + feature.properties.article_2_date + '</p><p><a href="' + feature.properties.article_3_url + '">' + feature.properties.article_3_headline + '</a><br>' + feature.properties.article_3_date + '</p></div><button type="button" class="btn btn-default popup-btn" id="btn">View More Articles!</button>'

    marker.bindPopup(popupContent);
};


map.on('popupclose', function(evt){
    $('#add-location').show();
    $('#fav-locations').show();
    $('#list-articles').hide();
});

map.on('popupopen', function(evt){ 
    // console.log("Popup opened!");
    $('#list-articles').show();
    $('.popup-btn').click(function(){
        c = evt.popup.getContent();
        c_str = c.slice(25,56);
        c_end = c_str.search("<");
        city = c_str.slice(0,c_end);
        geoj = popupsLayer.getGeoJSON();
        city_id = 0;
        for (var i = 0; i < geoj.features.length; i++) {
            if (city == geoj.features[i].properties.title) {
                console.log(geoj.features[i].properties.title, geoj.features[i].properties.description);
                cityUrl = geoj.features[i].properties.articleUrl;
            }
        }

        $.get(cityUrl, function(results){
            $('#list-articles').html(results);
            $('#add-location').hide();
            $('#fav-locations').hide();
        });
    });
});

map.on('popupclose', function(evt) {
    console.log("Popup closed!");
});
