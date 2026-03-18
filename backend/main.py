from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high", "critical"]


class EnvironmentalReading(BaseModel):
    city: str
    timestamp: datetime
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    precipitation: float | None = None
    air_quality_index: float | None = None
    pm25: float | None = None
    pm10: float | None = None
    water_level: float | None = None
    fire_danger_index: float | None = None


class RiskAssessment(BaseModel):
    overall_risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    risk_type_breakdown: Dict[str, float]
    summary: str
    recommendations: List[str]


class CurrentEnvironmentResponse(BaseModel):
    city: str
    reading: EnvironmentalReading
    risk: RiskAssessment


class QARequest(BaseModel):
    city: str
    question: str


class QAResponse(BaseModel):
    city: str
    answer: str


app = FastAPI(
    title="EcoGuardian API",
    description="Прототип сервиса мониторинга экологической обстановки.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_mock_reading(city: str) -> EnvironmentalReading:
    """Генерирует правдоподобные псевдо-данные для прототипа."""
    base_temp = random.uniform(-10, 35)
    humidity = random.uniform(20, 90)
    wind_speed = random.uniform(0, 15)
    precipitation = max(0.0, random.gauss(1, 2))

    pm25 = max(5.0, random.gauss(35, 15))
    pm10 = max(10.0, random.gauss(50, 20))
    aqi = max(0.0, min(500.0, pm25 * 1.2))

    water_level = max(0.0, random.gauss(1.5, 0.5))
    fire_index = max(0.0, min(100.0, 100 - humidity + max(0.0, base_temp - 20)))

    return EnvironmentalReading(
        city=city,
        timestamp=datetime.utcnow(),
        temperature=round(base_temp, 1),
        humidity=round(humidity, 1),
        wind_speed=round(wind_speed, 1),
        precipitation=round(precipitation, 1),
        air_quality_index=round(aqi, 1),
        pm25=round(pm25, 1),
        pm10=round(pm10, 1),
        water_level=round(water_level, 2),
        fire_danger_index=round(fire_index, 1),
    )


def compute_risk(reading: EnvironmentalReading) -> RiskAssessment:
    """Простейший движок оценки риска на базе порогов и весов."""

    def normalize(value: Optional[float], low: float, high: float) -> float:
        if value is None:
            return 0.0
        return max(0.0, min(1.0, (value - low) / (high - low)))

    fire_risk = normalize(reading.fire_danger_index, 20, 80)
    flood_risk = normalize(reading.water_level, 1.5, 3.0)
    air_risk = normalize(reading.air_quality_index, 50, 200)

    weights = {"fire": 0.4, "flood": 0.25, "air_pollution": 0.35}

    breakdown = {
        "fire": round(fire_risk * 100, 1),
        "flood": round(flood_risk * 100, 1),
        "air_pollution": round(air_risk * 100, 1),
    }

    score = (
        fire_risk * weights["fire"]
        + flood_risk * weights["flood"]
        + air_risk * weights["air_pollution"]
    ) * 100

    if score < 30:
        level: RiskLevel = "low"
    elif score < 60:
        level = "medium"
    elif score < 80:
        level = "high"
    else:
        level = "critical"

    # Для прототипа summary/recommendations зададим локально.
    summary = (
        f"В городе {reading.city} суммарный экологический риск оценивается как {level} "
        f"({score:.1f} из 100). Основные факторы: загрязнение воздуха — {breakdown['air_pollution']}%, "
        f"пожароопасность — {breakdown['fire']}%, риск подтоплений — {breakdown['flood']}%."
    )

    recs: List[str] = []
    if breakdown["air_pollution"] > 40:
        recs.append(
            "Снизьте время пребывания на улице, особенно при активных физических нагрузках."
        )
    if breakdown["fire"] > 40:
        recs.append(
            "Избегайте разведения открытого огня и сообщайте о задымлениях в экстренные службы."
        )
    if breakdown["flood"] > 40:
        recs.append(
            "Следите за сообщениями местных властей о подъёме уровня воды и возможной эвакуации."
        )
    if not recs:
        recs.append("Ситуация в целом благоприятная, соблюдайте обычные меры предосторожности.")

    return RiskAssessment(
        overall_risk_score=round(score, 1),
        risk_level=level,
        risk_type_breakdown=breakdown,
        summary=summary,
        recommendations=recs,
    )


@app.get("/api/environment/current", response_model=CurrentEnvironmentResponse)
def get_current_environment(city: str = "Moscow") -> CurrentEnvironmentResponse:
    """Текущая псевдо-обстановка и оценка риска для указанного города."""
    reading = generate_mock_reading(city)
    risk = compute_risk(reading)
    return CurrentEnvironmentResponse(city=city, reading=reading, risk=risk)


@app.post("/api/qa", response_model=QAResponse)
def ask_question(payload: QARequest) -> QAResponse:
    """
    Упрощённый Q&A-эндпоинт.

    Для прототипа формируем ответ на основе текущих данных и оценки риска
    без реального вызова LLM. Позже сюда можно интегрировать OpenAI.
    """
    reading = generate_mock_reading(payload.city)
    risk = compute_risk(reading)

    answer = (
        f"Вы спросили: «{payload.question}»\n\n"
        f"Текущая оценка риска для {payload.city}: {risk.risk_level} "
        f"({risk.overall_risk_score} из 100).\n"
        f"{risk.summary}\n\n"
        f"Рекомендации:\n- " + "\n- ".join(risk.recommendations)
    )

    return QAResponse(city=payload.city, answer=answer)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)

