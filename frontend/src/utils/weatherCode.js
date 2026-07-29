/**
 * Convert an Open-Meteo WMO weather code into
 * a readable description and visual symbol.
 */
export function getWeatherPresentation(weatherCode, isDay = true) {
  const code = Number(weatherCode);

  if (code === 0) {
    return {
      label: isDay ? "Clear sky" : "Clear night",
      icon: isDay ? "☀️" : "🌙",
    };
  }

  if ([1, 2].includes(code)) {
    return {
      label: "Partly cloudy",
      icon: isDay ? "🌤️" : "☁️",
    };
  }

  if (code === 3) {
    return {
      label: "Overcast",
      icon: "☁️",
    };
  }

  if ([45, 48].includes(code)) {
    return {
      label: "Fog",
      icon: "🌫️",
    };
  }

  if ([51, 53, 55, 56, 57].includes(code)) {
    return {
      label: "Drizzle",
      icon: "🌦️",
    };
  }

  if ([61, 63, 65, 66, 67, 80, 81, 82].includes(code)) {
    return {
      label: "Rain",
      icon: "🌧️",
    };
  }

  if ([71, 73, 75, 77, 85, 86].includes(code)) {
    return {
      label: "Snow",
      icon: "🌨️",
    };
  }

  if ([95, 96, 99].includes(code)) {
    return {
      label: "Thunderstorm",
      icon: "⛈️",
    };
  }

  return {
    label: "Weather unavailable",
    icon: "🌡️",
  };
}