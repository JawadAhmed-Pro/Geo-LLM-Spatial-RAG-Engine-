"use client";

import { useRef, useEffect, useState } from "react";
import Map, { Source, Layer, MapRef, Popup } from "react-map-gl/mapbox";
import bbox from "@turf/bbox";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

// Default to Swat view
const INITIAL_VIEW_STATE = {
  longitude: 72.35,
  latitude: 35.15,
  zoom: 8.5,
  pitch: 30,
  bearing: 0
};

export default function MapCanvas({ geojson }: { geojson: any | null }) {
  const mapRef = useRef<MapRef>(null);
  const [popupInfo, setPopupInfo] = useState<any | null>(null);

  // Animate map view to fit new data bounds
  useEffect(() => {
    if (geojson && geojson.features && geojson.features.length > 0) {
      try {
        const [minLng, minLat, maxLng, maxLat] = bbox(geojson);
        mapRef.current?.fitBounds(
          [[minLng, minLat], [maxLng, maxLat]],
          { padding: 100, duration: 2000, easing: (t) => t * (2 - t) }
        );
      } catch (err) {
        console.error("Error calculating bbox:", err);
      }
    }
    // Clear popup on new search
    setPopupInfo(null);
  }, [geojson]);

  const onMapClick = (event: any) => {
    const feature = event.features && event.features[0];
    if (feature) {
      setPopupInfo({
        longitude: event.lngLat.lng,
        latitude: event.lngLat.lat,
        properties: feature.properties
      });
    } else {
      setPopupInfo(null);
    }
  };

  if (!MAPBOX_TOKEN) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-neutral-900 text-neutral-400">
        <h2 className="text-xl font-medium mb-2">Mapbox Token Missing</h2>
        <p>Please add NEXT_PUBLIC_MAPBOX_TOKEN to your .env.local file.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      <Map
        ref={mapRef}
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={INITIAL_VIEW_STATE}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        interactiveLayerIds={['points-layer']}
        onClick={onMapClick}
      >
        {geojson && (
          <Source id="dynamic-data" type="geojson" data={geojson}>
            {/* 1. Rivers / Waterways (LineString) */}
            <Layer
              id="rivers-layer"
              type="line"
              paint={{
                'line-color': '#3b82f6', // blue-500
                'line-width': 2,
                'line-opacity': 0.8
              }}
              filter={['==', ['geometry-type'], 'LineString']}
            />

            {/* 2. Outline Glow for Points */}
            <Layer 
              id="points-glow"
              type="circle"
              paint={{
                'circle-radius': 14,
                'circle-color': '#10b981',
                'circle-opacity': 0.2,
                'circle-blur': 1
              }}
              filter={['==', ['geometry-type'], 'Point']}
            />
            {/* 3. Core Point Marker */}
            <Layer 
              id="points-layer"
              type="circle"
              paint={{
                'circle-radius': 6,
                'circle-color': '#10b981',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#064e3b' // emerald-950
              }}
              filter={['==', ['geometry-type'], 'Point']}
            />

            {/* 4. Polygon Layer fallback */}
            <Layer
              id="polygons-layer"
              type="fill"
              paint={{
                'fill-color': '#10b981',
                'fill-opacity': 0.2,
                'fill-outline-color': '#059669'
              }}
              filter={['any', ['==', ['geometry-type'], 'Polygon'], ['==', ['geometry-type'], 'MultiPolygon']]}
            />
          </Source>
        )}

        {/* Floating Legend */}
        <div className="absolute bottom-6 right-6 z-20 glass-container p-3 rounded-xl border border-neutral-800 text-[10px] font-bold uppercase tracking-wider space-y-2">
           <div className="flex items-center space-x-2">
             <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
             <span className="text-neutral-300">Active Facilities</span>
           </div>
           <div className="flex items-center space-x-2">
             <span className="w-3 h-1 bg-blue-500 rounded-full"></span>
             <span className="text-neutral-500">Hydrology Base</span>
           </div>
        </div>

        {popupInfo && (
          <Popup
            longitude={popupInfo.longitude}
            latitude={popupInfo.latitude}
            anchor="bottom"
            onClose={() => setPopupInfo(null)}
            closeButton={false}
          >
            <div className="bg-neutral-950 border border-neutral-800 text-neutral-100 p-3 rounded-xl shadow-2xl min-w-[150px] emerald-glow">
              <div className="text-emerald-500 text-[10px] font-bold uppercase tracking-widest mb-1">
                {popupInfo.properties.amenity || 'Facility'}
              </div>
              <div className="text-sm font-bold leading-tight mb-1">
                {popupInfo.properties.name || 'Unnamed'}
              </div>
              {popupInfo.properties.name_ur && (
                 <div className="text-xs text-neutral-400 font-medium" dir="rtl">
                   {popupInfo.properties.name_ur}
                 </div>
              )}
            </div>
          </Popup>
        )}
      </Map>
    </div>
  );
}
