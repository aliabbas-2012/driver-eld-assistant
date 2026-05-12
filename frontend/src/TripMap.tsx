import { MapContainer, Polyline, TileLayer, Popup, Marker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

type LngLat = [number, number]

function fixIcon() {
  const proto = L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown }
  delete proto._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  })
}
fixIcon()

export function TripMap({
  coordinates,
  labels,
}: {
  coordinates: LngLat[] | null | undefined
  labels?: { start?: string; pickup?: string; end?: string }
}) {
  if (!coordinates || coordinates.length < 2) {
    return (
      <div className="h-72 flex items-center justify-center rounded-xl bg-slate-100 text-slate-500 text-sm">
        Plan a trip to see the route on the map.
      </div>
    )
  }
  const latLngs = coordinates.map(([lng, lat]) => [lat, lng] as [number, number])
  const bounds = L.latLngBounds(latLngs)
  const mid = latLngs[Math.max(1, Math.floor(latLngs.length / 2))]

  return (
    <MapContainer
      bounds={bounds}
      boundsOptions={{ padding: [40, 40] }}
      className="h-72 w-full rounded-xl z-0"
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polyline positions={latLngs} color="#0ea5e9" weight={5} opacity={0.85} />
      {labels?.start && (
        <Marker position={latLngs[0]}>
          <Popup>{labels.start}</Popup>
        </Marker>
      )}
      {labels?.pickup && (
        <Marker position={mid}>
          <Popup>{labels.pickup}</Popup>
        </Marker>
      )}
      {labels?.end && (
        <Marker position={latLngs[latLngs.length - 1]}>
          <Popup>{labels.end}</Popup>
        </Marker>
      )}
    </MapContainer>
  )
}
