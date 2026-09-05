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

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [
          healthResponse,
          farmResponse,
          weatherResponse,
          advisoryResponse,
        ] = await Promise.all([
          fetch(`${apiBaseUrl}/api/health`),
          fetch(`${apiBaseUrl}/api/farms/1`),
          fetch(`${apiBaseUrl}/api/weather/1`),
          fetch(`${apiBaseUrl}/api/advisory/1`),
        ]);

        if (
          !healthResponse.ok ||
          !farmResponse.ok ||
          !weatherResponse.ok ||
          !advisoryResponse.ok
        ) {
          throw new Error("The backend returned an error.");
        }

        setHealth((await healthResponse.json()) as HealthResponse);
        setFarm((await farmResponse.json()) as Farm);
        setWeather((await weatherResponse.json()) as Weather);
        setAdvisory((await advisoryResponse.json()) as Advisory);
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

  return (
    <main className="container">
      <h1>AgroInfo</h1>
      <p>Initial frontend → FastAPI → MySQL milestone</p>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>System status</h2>
        <p>{health ? `FastAPI: ${health.status}` : "Checking FastAPI..."}</p>
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
