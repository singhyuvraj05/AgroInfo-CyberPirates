"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type HealthResponse = { status: string };

type Farm = {
  id: number;
  name: string;
  state: string;
  district: string;
  village: string;
  area_acres: number;
  soil_type: string;
  current_crop: string;
  latitude: number | null;
  longitude: number | null;
  soil_ph: number | null;
  nitrogen: number | null;
  phosphorus: number | null;
  potassium: number | null;
};

type Weather = {
  farm_id: number;
  location: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  forecast: {
    date: string;
    precipitation_sum: number;
    precipitation_probability_max: number | null;
  }[];
};

type Vegetation = {
  farm_id: number;
  ndvi: number;
  previous_ndvi: number;
  vegetation_status: string;
  trend: string;
  is_synthetic: boolean;
  note: string;
};

type Advisory = {
  farm_id: number;
  crop: string;
  risk_level: string;
  score: number;
  risks: string[];
  recommendations: string[];
  reasons: string[];
  confidence: number;
};

type Recommendations = {
  farm_id: number;
  location: string;
  assumptions: string[];
  recommendations: {
    crop: string;
    suitability_score: number;
    score_breakdown: Record<string, number>;
    reasons: string[];
    water_requirement: string;
    regenerative_benefit: string;
  }[];
};

type DiseaseScreening = {
  status: string;
  observation: string;
  certainty: string;
  next_step: string;
  is_demo: boolean;
  disclaimer: string;
};

type CooperativeInsight = {
  id: number;
  publisher_state: string;
  crop: string;
  insight_type: string;
  title: string;
  description: string;
  version: string;
  metric_label: string | null;
  metric_value: number | null;
  status: "published" | "adapted";
  source_insight_id: number | null;
  adaptation_note: string | null;
  created_at: string;
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const demoCoordinates = { lat: 20.0059, lng: 73.7897 };

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("The backend returned an error.");
  }
  return (await response.json()) as T;
}

function getErrorMessage(errorValue: unknown, fallback: string): string {
  return errorValue instanceof Error ? errorValue.message : fallback;
}

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [recommendations, setRecommendations] =
    useState<Recommendations | null>(null);
  const [vegetation, setVegetation] = useState<Vegetation | null>(null);
  const [cooperativeInsights, setCooperativeInsights] = useState<
    CooperativeInsight[]
  >([]);
  const [loadErrors, setLoadErrors] = useState<Record<string, string>>({});
  const [activeFarmId, setActiveFarmId] = useState(1);
  const [farmForm, setFarmForm] = useState({
    name: "",
    state: "",
    district: "",
    village: "",
    area_acres: "",
    soil_type: "",
    current_crop: "",
    soil_ph: "",
    nitrogen: "",
    phosphorus: "",
    potassium: "",
  });
  const [selectedCoordinates, setSelectedCoordinates] = useState(demoCoordinates);
  const [mapError, setMapError] = useState<string | null>(null);
  const [farmFormError, setFarmFormError] = useState<string | null>(null);
  const [farmFormMessage, setFarmFormMessage] = useState<string | null>(null);
  const [isCreatingFarm, setIsCreatingFarm] = useState(false);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.Marker | null>(null);

  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [screening, setScreening] = useState<DiseaseScreening | null>(null);
  const [screeningError, setScreeningError] = useState<string | null>(null);
  const [isScreening, setIsScreening] = useState(false);

  const [cooperativeError, setCooperativeError] = useState<string | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishState, setPublishState] = useState("Maharashtra");
  const [publishCrop, setPublishCrop] = useState("Soybean");
  const [publishType, setPublishType] = useState("advisory");
  const [publishTitle, setPublishTitle] = useState("");
  const [publishDescription, setPublishDescription] = useState("");
  const [publishMetricLabel, setPublishMetricLabel] = useState("");
  const [publishMetricValue, setPublishMetricValue] = useState("");
  const [publishVersion, setPublishVersion] = useState("v1");
  const [reuseState, setReuseState] = useState<Record<number, string>>({});
  const [reuseNotes, setReuseNotes] = useState<Record<number, string>>({});

  useEffect(() => {
    const requests: {
      key: string;
      request: Promise<unknown>;
      onSuccess: (value: unknown) => void;
    }[] = [
      {
        key: "health",
        request: fetchJson<HealthResponse>(`${apiBaseUrl}/api/health`),
        onSuccess: (value) => setHealth(value as HealthResponse),
      },
      {
        key: "farm",
        request: fetchJson<Farm>(`${apiBaseUrl}/api/farms/${activeFarmId}`),
        onSuccess: (value) => setFarm(value as Farm),
      },
      {
        key: "weather",
        request: fetchJson<Weather>(`${apiBaseUrl}/api/weather/${activeFarmId}`),
        onSuccess: (value) => setWeather(value as Weather),
      },
      {
        key: "advisory",
        request: fetchJson<Advisory>(`${apiBaseUrl}/api/advisory/${activeFarmId}`),
        onSuccess: (value) => setAdvisory(value as Advisory),
      },
      {
        key: "recommendations",
        request: fetchJson<Recommendations>(
          `${apiBaseUrl}/api/recommendations/${activeFarmId}`,
        ),
        onSuccess: (value) => setRecommendations(value as Recommendations),
      },
      {
        key: "vegetation",
        request: fetchJson<Vegetation>(`${apiBaseUrl}/api/vegetation/${activeFarmId}`),
        onSuccess: (value) => setVegetation(value as Vegetation),
      },
      {
        key: "cooperative",
        request: fetchJson<CooperativeInsight[]>(
          `${apiBaseUrl}/api/cooperative/insights`,
        ),
        onSuccess: (value) =>
          setCooperativeInsights(value as CooperativeInsight[]),
      },
    ];

    requests.forEach(({ key, request, onSuccess }) => {
      void request
        .then(onSuccess)
        .catch((errorValue: unknown) => {
          setLoadErrors((current) => ({
            ...current,
            [key]: getErrorMessage(errorValue, "Unable to load this section."),
          }));
        });
    });
  }, [activeFarmId]);

  useEffect(() => {
    const key = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    if (!key) {
      setMapError("Google Maps is unavailable. Enter coordinates manually below.");
      return;
    }

    function initializeMap() {
      if (!mapContainerRef.current || !window.google?.maps) {
        setMapError("Google Maps could not be loaded. Enter coordinates manually below.");
        return;
      }
      const map = new window.google.maps.Map(mapContainerRef.current, {
        center: selectedCoordinates,
        zoom: 8,
      });
      const marker = new window.google.maps.Marker({
        map,
        position: selectedCoordinates,
      });
      map.addListener("click", (event) => {
        if (!event.latLng) return;
        const coordinates = { lat: event.latLng.lat(), lng: event.latLng.lng() };
        setSelectedCoordinates(coordinates);
        marker.setPosition(coordinates);
      });
      mapRef.current = map;
      markerRef.current = marker;
      setMapError(null);
    }

    if (window.google?.maps) {
      initializeMap();
      return;
    }
    const existingScript = document.getElementById("google-maps-script");
    if (existingScript) {
      existingScript.addEventListener("load", initializeMap);
      existingScript.addEventListener("error", () =>
        setMapError("Google Maps could not be loaded. Enter coordinates manually below."),
      );
      return () => existingScript.removeEventListener("load", initializeMap);
    }
    const script = document.createElement("script");
    script.id = "google-maps-script";
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}`;
    script.async = true;
    script.defer = true;
    script.onload = initializeMap;
    script.onerror = () =>
      setMapError("Google Maps could not be loaded. Enter coordinates manually below.");
    document.head.appendChild(script);
  }, []);

  useEffect(() => {
    if (markerRef.current) markerRef.current.setPosition(selectedCoordinates);
  }, [selectedCoordinates]);

  function updateFarmField(field: keyof typeof farmForm, value: string) {
    setFarmForm((current) => ({ ...current, [field]: value }));
  }

  function useBrowserLocation() {
    if (!navigator.geolocation) {
      setMapError("Browser location is unavailable; select a point on the map.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coordinates = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        setSelectedCoordinates(coordinates);
        mapRef.current?.setCenter(coordinates);
      },
      () => setMapError("Location permission was unavailable; select a point on the map."),
    );
  }

  async function createFarm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFarmFormError(null);
    setFarmFormMessage(null);
    setIsCreatingFarm(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/farms`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...farmForm,
          area_acres: Number(farmForm.area_acres),
          latitude: selectedCoordinates.lat,
          longitude: selectedCoordinates.lng,
          soil_ph: Number(farmForm.soil_ph),
          nitrogen: Number(farmForm.nitrogen),
          phosphorus: Number(farmForm.phosphorus),
          potassium: Number(farmForm.potassium),
        }),
      });
      if (!response.ok) {
        const body = (await response.json()) as { detail?: string | { msg?: string }[] };
        const detail = Array.isArray(body.detail)
          ? body.detail.map((item) => item.msg ?? "Invalid value").join(", ")
          : body.detail;
        throw new Error(detail ?? "Unable to create the farm.");
      }
      const createdFarm = (await response.json()) as Farm;
      setActiveFarmId(createdFarm.id);
      setSelectedCoordinates({
        lat: createdFarm.latitude ?? selectedCoordinates.lat,
        lng: createdFarm.longitude ?? selectedCoordinates.lng,
      });
      setFarmFormMessage(`Farm created. Showing analysis for farm ID ${createdFarm.id}.`);
    } catch (errorValue) {
      setFarmFormError(getErrorMessage(errorValue, "Unable to create the farm."));
    } finally {
      setIsCreatingFarm(false);
    }
  }

  function useDemoFarm() {
    setActiveFarmId(1);
    setSelectedCoordinates(demoCoordinates);
    setFarmFormMessage("Using the demo farm (Farm ID 1).");
    setFarmFormError(null);
  }

  async function submitDiseaseScreening() {
    if (!selectedImage) {
      setScreeningError("Select a JPEG or PNG image first.");
      return;
    }
    if (!["image/jpeg", "image/png"].includes(selectedImage.type)) {
      setScreeningError("Only JPEG and PNG images are supported.");
      return;
    }
    if (selectedImage.size > 5 * 1024 * 1024) {
      setScreeningError("The image must be 5 MB or smaller.");
      return;
    }

    setIsScreening(true);
    setScreeningError(null);
    setScreening(null);
    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await fetch(`${apiBaseUrl}/api/disease-screening`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const body = (await response.json()) as { detail?: string };
        throw new Error(body.detail ?? "Unable to screen the image.");
      }
      setScreening((await response.json()) as DiseaseScreening);
    } catch (errorValue) {
      setScreeningError(
        getErrorMessage(errorValue, "Unable to screen the image."),
      );
    } finally {
      setIsScreening(false);
    }
  }

  async function publishInsight() {
    setIsPublishing(true);
    setCooperativeError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/api/cooperative/insights`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          publisher_state: publishState,
          crop: publishCrop,
          insight_type: publishType,
          title: publishTitle,
          description: publishDescription,
          version: publishVersion,
          metric_label: publishMetricLabel || null,
          metric_value: publishMetricValue ? Number(publishMetricValue) : null,
        }),
      });
      if (!response.ok) {
        throw new Error("Unable to publish the cooperative insight.");
      }
      const insight = (await response.json()) as CooperativeInsight;
      setCooperativeInsights((current) => [...current, insight]);
      setPublishTitle("");
      setPublishDescription("");
      setPublishMetricLabel("");
      setPublishMetricValue("");
    } catch (errorValue) {
      setCooperativeError(
        getErrorMessage(
          errorValue,
          "Unable to publish the cooperative insight.",
        ),
      );
    } finally {
      setIsPublishing(false);
    }
  }

  async function reuseInsight(insightId: number) {
    setCooperativeError(null);
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/cooperative/insights/${insightId}/reuse`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            target_state: reuseState[insightId] ?? "",
            adaptation_note: reuseNotes[insightId] ?? "",
          }),
        },
      );
      if (!response.ok) {
        throw new Error("Unable to reuse the cooperative insight.");
      }
      const adapted = (await response.json()) as CooperativeInsight;
      setCooperativeInsights((current) => [...current, adapted]);
    } catch (errorValue) {
      setCooperativeError(
        getErrorMessage(
          errorValue,
          "Unable to reuse the cooperative insight.",
        ),
      );
    }
  }

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">AgroInfo</p>
          <h1>Farmer Decision Dashboard</h1>
          <p className="subtitle">
            Practical field context, transparent signals, and next steps in one
            place.
          </p>
        </div>
        <div className="header-status">
          <span className={`status-dot ${health ? "online" : ""}`} />
          {health ? "FastAPI connected" : "Connecting..."}
        </div>
      </header>

      <section className="secondary-panel farm-setup-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Live setup</p>
            <h2>Analyze your farm</h2>
          </div>
          <span className="badge prototype">Farm ID {activeFarmId}</span>
        </div>
        <p className="section-help">
          Add your farm and soil details. The map selects a latitude/longitude
          point only; it does not measure boundaries or determine suitability.
        </p>
        <form className="farm-setup-form" onSubmit={createFarm}>
          <div className="form-grid">
            {([
              ["name", "Farm name"],
              ["state", "State"],
              ["district", "District"],
              ["village", "Village"],
              ["area_acres", "Area (acres)"],
              ["soil_type", "Soil type"],
              ["current_crop", "Current crop"],
              ["soil_ph", "Soil pH"],
              ["nitrogen", "Nitrogen"],
              ["phosphorus", "Phosphorus"],
              ["potassium", "Potassium"],
            ] as const).map(([field, label]) => (
              <label key={field}>
                {label}
                <input
                  required
                  type={["area_acres", "soil_ph", "nitrogen", "phosphorus", "potassium"].includes(field) ? "number" : "text"}
                  step="any"
                  value={farmForm[field]}
                  onChange={(event) => updateFarmField(field, event.target.value)}
                />
              </label>
            ))}
          </div>
          <div className="map-picker">
            <div className="map-heading">
              <h3>Farm location</h3>
              <button type="button" onClick={useBrowserLocation}>Use my location</button>
            </div>
            <div className="map-container" ref={mapContainerRef} />
            {mapError && (
              <>
                <p className="section-message">{mapError}</p>
                <div className="coordinate-fallback">
                  <label>
                    Latitude
                    <input
                      type="number"
                      step="any"
                      value={selectedCoordinates.lat}
                      onChange={(event) => setSelectedCoordinates((current) => ({ ...current, lat: Number(event.target.value) }))}
                    />
                  </label>
                  <label>
                    Longitude
                    <input
                      type="number"
                      step="any"
                      value={selectedCoordinates.lng}
                      onChange={(event) => setSelectedCoordinates((current) => ({ ...current, lng: Number(event.target.value) }))}
                    />
                  </label>
                </div>
              </>
            )}
            {!mapError && (
              <div className="selected-coordinates" aria-live="polite">
                Selected coordinates: <strong>{selectedCoordinates.lat.toFixed(6)}, {selectedCoordinates.lng.toFixed(6)}</strong>
              </div>
            )}
          </div>
          {farmFormError && <p className="error">{farmFormError}</p>}
          {farmFormMessage && <p className="success-message">{farmFormMessage}</p>}
          <div className="farm-actions">
            <button className="button-primary" disabled={isCreatingFarm} type="submit">
              {isCreatingFarm ? "Creating farm..." : "Analyze my farm"}
            </button>
            <button type="button" onClick={useDemoFarm}>Use demo farm</button>
          </div>
        </form>
      </section>

      <section className="farm-banner">
        {farm ? (
          <>
            <div>
              <p className="eyebrow">Your farm</p>
              <h2>{farm.name}</h2>
              <p>
                {farm.village}, {farm.district}, {farm.state}
              </p>
            </div>
            <div className="farm-facts">
              <span>
                <strong>Crop</strong>
                {farm.current_crop}
              </span>
              <span>
                <strong>Area</strong>
                {farm.area_acres} acres
              </span>
              <span>
                <strong>Soil</strong>
                {farm.soil_type}
              </span>
            </div>
          </>
        ) : (
          <SectionMessage
            message={
              loadErrors.farm ?? "Loading farm context..."
            }
          />
        )}
      </section>

      <section>
        <div className="section-heading">
          <div>
            <p className="eyebrow">At a glance</p>
            <h2>Current conditions</h2>
          </div>
          <p className="section-help">Signals refresh from the existing AgroInfo services.</p>
        </div>
        <div className="summary-grid">
          <article className="summary-card">
            <div className="card-heading">
              <h3>Weather</h3>
              <span className="badge live">Live</span>
            </div>
            {weather ? (
              <>
                <p className="metric-large">{weather.temperature}°C</p>
                <div className="metric-row">
                  <span>Humidity<strong>{weather.humidity}%</strong></span>
                  <span>Rain now<strong>{weather.precipitation} mm</strong></span>
                </div>
                <p className="muted">
                  Next rain: {weather.forecast[0]?.precipitation_sum ?? 0} mm
                  {weather.forecast[0]?.precipitation_probability_max === null ||
                  weather.forecast[0]?.precipitation_probability_max === undefined
                    ? ""
                    : ` · ${weather.forecast[0].precipitation_probability_max}% chance`}
                </p>
              </>
            ) : (
              <SectionMessage message={loadErrors.weather ?? "Loading weather..."} />
            )}
          </article>

          <article className="summary-card">
            <div className="card-heading">
              <h3>Vegetation</h3>
              <span className="badge demo">Synthetic/demo</span>
            </div>
            {vegetation ? (
              <>
                <p className="metric-large">{vegetation.ndvi} <small>NDVI</small></p>
                <div className="metric-row">
                  <span>Status<strong>{vegetation.vegetation_status}</strong></span>
                  <span>Trend<strong>{vegetation.trend}</strong></span>
                </div>
                <p className="muted">Synthetic/demo vegetation signal.</p>
              </>
            ) : (
              <SectionMessage
                message={loadErrors.vegetation ?? "Loading vegetation..."}
              />
            )}
          </article>

          <article className="summary-card">
            <div className="card-heading">
              <h3>Advisory status</h3>
              <span className="badge prototype">Rule-based</span>
            </div>
            {advisory ? (
              <>
                <p className={`risk-value ${advisory.risk_level}`}>
                  {advisory.risk_level} risk
                </p>
                <div className="metric-row">
                  <span>Signal<strong>{advisory.score} points</strong></span>
                  <span>Indicator<strong>{Math.round(advisory.confidence * 100)}%</strong></span>
                </div>
                <p className="muted">
                  Transparent prototype rule-based advisory. Indicator is not
                  scientific certainty.
                </p>
              </>
            ) : (
              <SectionMessage message={loadErrors.advisory ?? "Loading advisory..."} />
            )}
          </article>
        </div>
      </section>

      <section className="primary-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Field guidance</p>
            <h2>What to do now</h2>
          </div>
          <p className="section-help">
            Transparent prototype rules combine available farm, soil, and
            weather information.
          </p>
        </div>
        {advisory ? (
          <div className="advisory-layout">
            <div className={`risk-panel ${advisory.risk_level}`}>
              <span>Overall risk</span>
              <strong>{advisory.risk_level}</strong>
              <small>{advisory.score} points · prototype signal</small>
            </div>
            <div>
              <h3>Why this matters</h3>
              <ul>
                {advisory.reasons.map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            </div>
            <div>
              <h3>Recommended actions</h3>
              <ul>
                {advisory.recommendations.map((action) => <li key={action}>{action}</li>)}
              </ul>
            </div>
          </div>
        ) : (
          <SectionMessage message={loadErrors.advisory ?? "Loading field guidance..."} />
        )}
      </section>

      <section>
        <div className="section-heading">
          <div>
            <p className="eyebrow">Planning options</p>
            <h2>Crop &amp; regenerative recommendations</h2>
          </div>
          <p className="section-help">
            Prototype suitability score — not a probability or yield prediction.
          </p>
        </div>
        {recommendations ? (
          <div className="recommendation-grid">
            {recommendations.recommendations.map((recommendation) => (
              <article className="recommendation-card" key={recommendation.crop}>
                <div className="card-heading">
                  <h3>{recommendation.crop}</h3>
                  <strong className="score-pill">{recommendation.suitability_score}/100</strong>
                </div>
                <p className="score-label">
                  Prototype suitability score — not a probability or yield prediction.
                </p>
                <ul>
                  {recommendation.reasons.slice(0, 2).map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
                <p><strong>Water:</strong> {recommendation.water_requirement} <span className="muted">(informational)</span></p>
                <p><strong>Regenerative note:</strong> {recommendation.regenerative_benefit}</p>
              </article>
            ))}
          </div>
        ) : (
          <SectionMessage
            message={loadErrors.recommendations ?? "Loading recommendations..."}
          />
        )}
      </section>

      <section className="secondary-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Optional tool</p>
            <h2>Optional Leaf Image Screening</h2>
          </div>
          <span className="badge prototype">Prototype only</span>
        </div>
        <p className="section-help">
          Upload a clear JPEG or PNG for a constrained workflow demonstration.
          This is not a real disease diagnosis.
        </p>
        <div className="upload-row">
          <input
            accept="image/jpeg,image/png"
            aria-label="Leaf image"
            onChange={(event) => {
              setSelectedImage(event.target.files?.[0] ?? null);
              setScreening(null);
              setScreeningError(null);
            }}
            type="file"
          />
          <button
            className="button-primary"
            disabled={isScreening}
            onClick={() => void submitDiseaseScreening()}
            type="button"
          >
            {isScreening ? "Screening..." : "Upload and screen"}
          </button>
        </div>
        {screeningError && <p className="error">{screeningError}</p>}
        {screening && (
          <div className="screening-result">
            <p><strong>Status:</strong> {screening.status}</p>
            <p><strong>Observation:</strong> {screening.observation}</p>
            <p><strong>Prototype certainty:</strong> {screening.certainty}</p>
            <p><strong>Suggested next step:</strong> {screening.next_step}</p>
            <p className="note">{screening.disclaimer}</p>
          </div>
        )}
      </section>

      <section className="secondary-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Shared learning</p>
            <h2>Prototype Cooperative Knowledge Registry</h2>
          </div>
          <span className="badge demo">Fictional demo records</span>
        </div>
        <p className="section-help">
          Publish, discover, and adapt linked snapshots. This is not real
          cross-state federation, authentication, or institutional verification.
        </p>
        <h3>Publish an insight</h3>
        <div className="form-grid">
          <input value={publishState} onChange={(event) => setPublishState(event.target.value)} placeholder="Publisher state" aria-label="Publisher state" />
          <input value={publishCrop} onChange={(event) => setPublishCrop(event.target.value)} placeholder="Crop" aria-label="Crop" />
          <select value={publishType} onChange={(event) => setPublishType(event.target.value)} aria-label="Insight type">
            <option value="advisory">Advisory</option>
            <option value="crop_recommendation">Crop recommendation</option>
            <option value="vegetation">Vegetation</option>
            <option value="disease_screening">Disease screening</option>
          </select>
          <input value={publishVersion} onChange={(event) => setPublishVersion(event.target.value)} placeholder="Version" aria-label="Version" />
          <input value={publishTitle} onChange={(event) => setPublishTitle(event.target.value)} placeholder="Insight title" aria-label="Insight title" />
          <input value={publishMetricLabel} onChange={(event) => setPublishMetricLabel(event.target.value)} placeholder="Metric label (optional)" aria-label="Metric label" />
          <input value={publishMetricValue} onChange={(event) => setPublishMetricValue(event.target.value)} placeholder="Metric value (optional)" aria-label="Metric value" type="number" />
        </div>
        <textarea value={publishDescription} onChange={(event) => setPublishDescription(event.target.value)} placeholder="Describe the prototype insight" aria-label="Insight description" />
        <button className="button-primary" disabled={isPublishing} onClick={() => void publishInsight()} type="button">
          {isPublishing ? "Publishing..." : "Publish insight"}
        </button>
        {cooperativeError && <p className="error">{cooperativeError}</p>}
        <h3 className="registry-heading">Discover shared records</h3>
        {cooperativeInsights.length ? (
          <div className="registry-list">
            {cooperativeInsights.map((insight) => (
              <article className="registry-item" key={insight.id}>
                <div className="registry-title">
                  <h4>{insight.title}</h4>
                  <span className={`badge ${insight.status === "adapted" ? "adapted" : "published"}`}>
                    {insight.status}
                  </span>
                </div>
                <p className="registry-meta">
                  <strong>{insight.publisher_state}</strong> · {insight.crop} · {insight.insight_type}
                </p>
                <p>{insight.description}</p>
                <p className="muted">
                  Version {insight.version}
                  {insight.metric_label
                    ? ` · ${insight.metric_label}: ${insight.metric_value}`
                    : ""}
                </p>
                {insight.source_insight_id && (
                  <p className="relationship">
                    Adapted from insight #{insight.source_insight_id}
                    {insight.adaptation_note ? ` · ${insight.adaptation_note}` : ""}
                  </p>
                )}
                {insight.status === "published" && (
                  <div className="reuse-row">
                    <input
                      value={reuseState[insight.id] ?? ""}
                      onChange={(event) => setReuseState((current) => ({ ...current, [insight.id]: event.target.value }))}
                      placeholder="Target state"
                      aria-label={`Target state for ${insight.title}`}
                    />
                    <input
                      value={reuseNotes[insight.id] ?? ""}
                      onChange={(event) => setReuseNotes((current) => ({ ...current, [insight.id]: event.target.value }))}
                      placeholder="Adaptation note"
                      aria-label={`Adaptation note for ${insight.title}`}
                    />
                    <button onClick={() => void reuseInsight(insight.id)} type="button">Reuse / adapt</button>
                  </div>
                )}
              </article>
            ))}
          </div>
        ) : (
          <SectionMessage
            message={loadErrors.cooperative ?? "No shared records available."}
          />
        )}
      </section>

      <footer className="dashboard-footer">
        <span className={`status-dot ${health ? "online" : ""}`} />
        <span>{health ? `Backend status: ${health.status}` : "Backend status unavailable"}</span>
        <span className="footer-note">AgroInfo prototype dashboard · demo and heuristic signals are labeled throughout.</span>
      </footer>
    </main>
  );
}

function SectionMessage({ message }: { message: string }) {
  return <p className="section-message">{message}</p>;
}
