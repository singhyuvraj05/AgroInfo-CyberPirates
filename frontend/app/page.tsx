"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
};

type Farm = {
  id: number;
  name: string;
  state: string;
  district: string;
  village: string;
  area_acres: number;
  soil_type: string;
  current_crop: string;
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

type DiseaseScreening = {
  status: string;
  observation: string;
  certainty: string;
  next_step: string;
  is_demo: boolean;
  disclaimer: string;
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

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [recommendations, setRecommendations] =
    useState<Recommendations | null>(null);
  const [vegetation, setVegetation] = useState<Vegetation | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [screening, setScreening] = useState<DiseaseScreening | null>(null);
  const [screeningError, setScreeningError] = useState<string | null>(null);
  const [isScreening, setIsScreening] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [
          healthResponse,
          farmResponse,
          weatherResponse,
          advisoryResponse,
          recommendationsResponse,
          vegetationResponse,
        ] = await Promise.all([
          fetch(`${apiBaseUrl}/api/health`),
          fetch(`${apiBaseUrl}/api/farms/1`),
          fetch(`${apiBaseUrl}/api/weather/1`),
          fetch(`${apiBaseUrl}/api/advisory/1`),
          fetch(`${apiBaseUrl}/api/recommendations/1`),
          fetch(`${apiBaseUrl}/api/vegetation/1`),
        ]);

        if (
          !healthResponse.ok ||
          !farmResponse.ok ||
          !weatherResponse.ok ||
          !advisoryResponse.ok
          || !recommendationsResponse.ok ||
          !vegetationResponse.ok
        ) {
          throw new Error("The backend returned an error.");
        }

        setHealth((await healthResponse.json()) as HealthResponse);
        setFarm((await farmResponse.json()) as Farm);
        setWeather((await weatherResponse.json()) as Weather);
        setAdvisory((await advisoryResponse.json()) as Advisory);
        setRecommendations(
          (await recommendationsResponse.json()) as Recommendations,
        );
        setVegetation((await vegetationResponse.json()) as Vegetation);
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to connect to the backend.",
        );
      }
    }

    void loadData();
  }, []);

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
    } catch (requestError) {
      setScreeningError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to screen the image.",
      );
    } finally {
      setIsScreening(false);
    }
  }

  return (
    <main className="container">
      <h1>AgroInfo</h1>
      <p>Initial frontend → FastAPI → MySQL milestone</p>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Constrained disease screening prototype</h2>
        <p className="note">
          This accepts an image for a demo workflow only. It is not an AI
          classifier or a validated disease diagnosis system.
        </p>
        <input
          accept="image/jpeg,image/png"
          onChange={(event) => {
            setSelectedImage(event.target.files?.[0] ?? null);
            setScreening(null);
            setScreeningError(null);
          }}
          type="file"
        />
        <button
          className="screen-button"
          disabled={isScreening}
          onClick={() => void submitDiseaseScreening()}
          type="button"
        >
          {isScreening ? "Screening image..." : "Upload and screen"}
        </button>
        {screeningError && <p className="error">{screeningError}</p>}
        {screening && (
          <div className="screening-result">
            <p>Status: {screening.status}</p>
            <p>Observation: {screening.observation}</p>
            <p>Prototype certainty: {screening.certainty}</p>
            <p>Suggested next step: {screening.next_step}</p>
            <p className="note">{screening.disclaimer}</p>
          </div>
        )}
      </section>

      <section className="card">
        <h2>System status</h2>
        <p>{health ? `FastAPI: ${health.status}` : "Checking FastAPI..."}</p>
      </section>

      <section className="card">
        <h2>Vegetation health</h2>
        {vegetation ? (
          <>
            <p className="note">Synthetic/demo data</p>
            <dl>
              <dt>Current NDVI</dt>
              <dd>{vegetation.ndvi}</dd>
              <dt>Previous NDVI</dt>
              <dd>{vegetation.previous_ndvi}</dd>
              <dt>Vegetation status</dt>
              <dd>{vegetation.vegetation_status}</dd>
              <dt>Trend</dt>
              <dd>{vegetation.trend}</dd>
            </dl>
            <p>{vegetation.note}</p>
          </>
        ) : (
          <p>Loading vegetation health...</p>
        )}
      </section>

      <section className="card">
        <h2>Crop and regenerative recommendations</h2>
        {recommendations ? (
          <>
            <p>{recommendations.location}</p>
            <p className="note">
              Suitability scores are deterministic MVP heuristics, not
              probabilities or yield predictions.
            </p>
            {recommendations.recommendations.map((recommendation) => (
              <article key={recommendation.crop}>
                <h3>
                  {recommendation.crop}: {recommendation.suitability_score}/100
                </h3>
                <p>Water requirement: {recommendation.water_requirement}</p>
                <ul>
                  {recommendation.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
                <p>
                  Regenerative note: {recommendation.regenerative_benefit}
                </p>
              </article>
            ))}
          </>
        ) : (
          <p>Loading recommendations...</p>
        )}
      </section>

      <section className="card">
        <h2>Agricultural advisory</h2>
        {advisory ? (
          <>
            <p>
              Overall risk: <strong>{advisory.risk_level}</strong> (
              {advisory.score} points)
            </p>
            <p>Confidence: {Math.round(advisory.confidence * 100)}%</p>
            <h3>Reasons</h3>
            <ul>
              {advisory.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
            <h3>Recommended actions</h3>
            <ul>
              {advisory.recommendations.map((recommendation) => (
                <li key={recommendation}>{recommendation}</li>
              ))}
            </ul>
          </>
        ) : (
          <p>Loading advisory...</p>
        )}
      </section>

      <section className="card">
        <h2>Weather</h2>
        {weather ? (
          <>
            <p>{weather.location}</p>
            <dl>
              <dt>Temperature</dt>
              <dd>{weather.temperature} °C</dd>
              <dt>Humidity</dt>
              <dd>{weather.humidity}%</dd>
              <dt>Current precipitation</dt>
              <dd>{weather.precipitation} mm</dd>
            </dl>
            <h3>Three-day precipitation forecast</h3>
            <ul>
              {weather.forecast.map((day) => (
                <li key={day.date}>
                  {day.date}: {day.precipitation_sum} mm
                  {day.precipitation_probability_max === null
                    ? ""
                    : ` (${day.precipitation_probability_max}% chance)`}
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p>Loading weather...</p>
        )}
      </section>

      <section className="card">
        <h2>Demo farm</h2>
        {farm ? (
          <dl>
            <dt>Name</dt>
            <dd>{farm.name}</dd>
            <dt>Location</dt>
            <dd>
              {farm.village}, {farm.district}, {farm.state}
            </dd>
            <dt>Area</dt>
            <dd>{farm.area_acres} acres</dd>
            <dt>Soil</dt>
            <dd>{farm.soil_type}</dd>
            <dt>Current crop</dt>
            <dd>{farm.current_crop}</dd>
          </dl>
        ) : (
          <p>Loading farm data...</p>
        )}
      </section>
    </main>
  );
}
