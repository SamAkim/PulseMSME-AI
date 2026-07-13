import type { RiskBand } from "./types";

interface BandStyle {
  text: string;
  bg: string;
  fg: string;
}

const BAND_STYLES: Record<RiskBand, BandStyle> = {
  "High Risk": { text: "High Risk", bg: "var(--color-band-highrisk-bg)", fg: "var(--color-band-highrisk)" },
  Bad: { text: "Bad", bg: "var(--color-band-bad-bg)", fg: "var(--color-band-bad)" },
  Average: { text: "Average", bg: "var(--color-band-average-bg)", fg: "var(--color-band-average)" },
  Good: { text: "Good", bg: "var(--color-band-good-bg)", fg: "var(--color-band-good)" },
  Excellent: { text: "Excellent", bg: "var(--color-band-excellent-bg)", fg: "var(--color-band-excellent)" },
};

export function bandStyle(band: RiskBand): BandStyle {
  return BAND_STYLES[band];
}

export function bandColorHex(band: RiskBand): string {
  const map: Record<RiskBand, string> = {
    "High Risk": "#a4342a",
    Bad: "#b5641f",
    Average: "#9a7b0a",
    Good: "#2b7a5b",
    Excellent: "#146356",
  };
  return map[band];
}
