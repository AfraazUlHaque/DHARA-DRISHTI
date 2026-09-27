import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  ImageOverlay,
  LayersControl,
  ZoomControl,
  ScaleControl,
  GeoJSON,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./MapViewer.css";

const { BaseLayer, Overlay } = LayersControl;

const API_BASE = "http://127.0.0.1:8000";

const rasterBounds = {
  satellite: [
    [17.16570939055315, 80.33086469572562],
    [17.8343666578826, 80.83390502520248],
  ] as [[number, number], [number, number]],

  ndvi: [
    [17.16570939055315, 80.33086469572562],
    [17.8343666578826, 80.83390502520248],
  ] as [[number, number], [number, number]],

  water: [
    [17.16570939055315, 80.33086469572562],
    [17.8343666578826, 80.83390502520248],
  ] as [[number, number], [number, number]],

  lulc: [
    [17.16570939055315, 80.33086469572562],
    [17.8343666578826, 80.83390502520248],
  ] as [[number, number], [number, number]],

  drainage: [
    [17.166805555555552, 80.33319444444444],
    [17.83347222222222, 80.83319444444444],
  ] as [[number, number], [number, number]],

  slope: [
    [17.166805555555552, 80.33319444444444],
    [17.83347222222222, 80.83319444444444],
  ] as [[number, number], [number, number]],

  erosion: [
    [17.166805555555552, 80.33319444444444],
    [17.83347222222222, 80.83319444444444],
  ] as [[number, number], [number, number]],

  intervention: [
    [17.166805555555552, 80.33319444444444],
    [17.83347222222222, 80.83319444444444],
  ] as [[number, number], [number, number]],

  health: [
    [17.166805555555552, 80.33319444444444],
    [17.83347222222222, 80.83319444444444],
  ] as [[number, number], [number, number]],
};

function MapViewer() {
  const center: [number, number] = [17.5, 80.58];

  // ============================================================
  // MURREDU WATERSHED BOUNDARY
  // ============================================================

  const [murreduBoundary, setMurreduBoundary] = useState<any>(null);

  useEffect(() => {
    let mounted = true;

    fetch(`${API_BASE}/murredu-boundary`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `Murredu boundary request failed: ${response.status}`
          );
        }

        return response.json();
      })
      .then((data) => {
        if (mounted && data?.status === "success" && data?.boundary) {
  setMurreduBoundary({
    type: "Feature",
    geometry: data.boundary,
    properties: data.properties || {},
  });
}
      })
      .catch((error) => {
        console.error("Murredu boundary:", error);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="gis-map-wrapper">

      <MapContainer
        center={center}
        zoom={10}
        minZoom={8}
        maxZoom={16}
        zoomControl={false}
        className="gis-map"
      >

        {/* ================= BASE MAP ================= */}

        <LayersControl position="topright">

          <BaseLayer checked name="Street Map">

            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

          </BaseLayer>

          <BaseLayer name="Satellite">

            <TileLayer
              attribution="Tiles &copy; Esri"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />

          </BaseLayer>


          {/* ================= NDVI ================= */}

          <Overlay checked name="NDVI / Vegetation">

            <ImageOverlay
              url="/layers/ndvi.png"
              bounds={rasterBounds.ndvi}
              opacity={0.65}
              zIndex={20}
            />

          </Overlay>


          {/* ================= WATER ================= */}

          <Overlay name="Water Bodies">

            <ImageOverlay
              url="/layers/water.png"
              bounds={rasterBounds.water}
              opacity={0.75}
              zIndex={30}
            />

          </Overlay>


          {/* ================= LULC ================= */}

          <Overlay name="Land Use / Land Cover">

            <ImageOverlay
              url="/layers/lulc.png"
              bounds={rasterBounds.lulc}
              opacity={0.55}
              zIndex={15}
            />

          </Overlay>


          {/* ================= DRAINAGE ================= */}

          <Overlay name="Drainage Network">

            <ImageOverlay
              url="/layers/drainage.png"
              bounds={rasterBounds.drainage}
              opacity={0.90}
              zIndex={40}
            />

          </Overlay>


          {/* ================= SLOPE ================= */}

          <Overlay name="Slope">

            <ImageOverlay
              url="/layers/slope.png"
              bounds={rasterBounds.slope}
              opacity={0.45}
              zIndex={12}
            />

          </Overlay>


          {/* ================= EROSION ================= */}

          <Overlay name="Erosion Risk">

            <ImageOverlay
              url="/layers/erosion.png"
              bounds={rasterBounds.erosion}
              opacity={0.55}
              zIndex={50}
            />

          </Overlay>


          {/* ================= INTERVENTION ================= */}

          <Overlay name="Intervention Priority">

            <ImageOverlay
              url="/layers/intervention.png"
              bounds={rasterBounds.intervention}
              opacity={0.65}
              zIndex={60}
            />

          </Overlay>


          {/* ================= HEALTH ================= */}

          <Overlay name="Watershed Health Index">

            <ImageOverlay
              url="/layers/health.png"
              bounds={rasterBounds.health}
              opacity={0.50}
              zIndex={10}
            />

          </Overlay>

        </LayersControl>


        {/* ====================================================== */}
        {/* MURREDU WATERSHED BOUNDARY */}
        {/* ====================================================== */}

        {murreduBoundary && (
          <GeoJSON
            data={murreduBoundary}
            style={{
              color: "#14532d",
              weight: 3,
              opacity: 1,
              fillOpacity: 0,
            }}
          />
        )}


        {/* ================= MAP CONTROLS ================= */}

        <ZoomControl position="topleft" />

        <ScaleControl position="bottomleft" />

      </MapContainer>


      {/* ================= MAP TITLE ================= */}

      <div className="map-title-box">

        <strong>Murredu Watershed</strong>

        <span>
          Telangana — Geospatial Monitoring Viewer
        </span>

      </div>


      {/* ================= COORDINATES ================= */}

      <div className="coordinate-box">

        <strong>Study Extent</strong>

        <span>
          Latitude: 17.1657°N – 17.8344°N
        </span>

        <span>
          Longitude: 80.3309°E – 80.8339°E
        </span>

      </div>


      {/* ================= LEGEND ================= */}

      <div className="map-legend">

        <strong>Map Legend</strong>

        <div>
          <span className="legend-box vegetation"></span>
          Vegetation
        </div>

        <div>
          <span className="legend-box water"></span>
          Water Bodies
        </div>

        <div>
          <span className="legend-box erosion"></span>
          Erosion Risk
        </div>

        <div>
          <span className="legend-box intervention"></span>
          Intervention Priority
        </div>

      </div>

    </div>
  );
}

export default MapViewer;