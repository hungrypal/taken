// This map visualizes real farm coordinates and supports a click-selected location for forms.
import { MapContainer, Marker, TileLayer, useMapEvents } from "react-leaflet";
import type { Farm } from "../types/api";
import L from "leaflet";
import { useEffect } from "react";

const markerIcon = L.divIcon({ className: "", html: '<div style="width:16px;height:16px;border-radius:50%;background:#14b8a6;border:3px solid white;box-shadow:0 0 0 2px #0f766e"></div>', iconSize: [16, 16], iconAnchor: [8, 8] });
function ClickHandler({ onSelect }: { onSelect?: (latitude: number, longitude: number) => void }) { useMapEvents({ click: (event) => onSelect?.(event.latlng.lat, event.latlng.lng) }); return null; }
function Recenter({ latitude, longitude }: { latitude: number; longitude: number }) { const map = useMapEvents({}); useEffect(() => { map.setView([latitude, longitude]); }, [latitude, longitude, map]); return null; }
export function FarmMap({ farms = [], latitude = 28.4, longitude = 77, onSelect }: { farms?: Farm[]; latitude?: number; longitude?: number; onSelect?: (latitude: number, longitude: number) => void }) { return <div className="h-80 overflow-hidden rounded-xl"><MapContainer center={[latitude, longitude]} zoom={6} className="h-full w-full" scrollWheelZoom><TileLayer attribution="© OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" /><Recenter latitude={latitude} longitude={longitude} /><ClickHandler onSelect={onSelect} />{farms.map((farm) => <Marker key={farm.id} position={[farm.latitude, farm.longitude]} icon={markerIcon} />)}</MapContainer></div>; }
