declare module "*.css";

declare namespace google.maps {
  class Map {
    constructor(element: HTMLElement, options: { center: LatLngLiteral; zoom: number });
    addListener(eventName: string, handler: (event: MapMouseEvent) => void): void;
    setCenter(center: LatLngLiteral): void;
  }

  class Marker {
    constructor(options: { map: Map; position: LatLngLiteral });
    setPosition(position: LatLngLiteral): void;
  }

  type LatLngLiteral = { lat: number; lng: number };
  type MapMouseEvent = { latLng: { lat(): number; lng(): number } | null };
}

interface Window {
  google?: typeof google;
}
