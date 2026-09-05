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

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [healthResponse, farmResponse] = await Promise.all([
          fetch(`${apiBaseUrl}/api/health`),
          fetch(`${apiBaseUrl}/api/farms/1`),
        ]);

        if (!healthResponse.ok || !farmResponse.ok) {
          throw new Error("The backend returned an error.");
        }

        setHealth((await healthResponse.json()) as HealthResponse);
        setFarm((await farmResponse.json()) as Farm);
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
