import type { EVMStatus } from "@/types/evm.types";

interface StatusVisual {
  color: string;
  background: string;
}

/**
 * Single source of truth for the semáforo palette. Components consume
 * these tokens instead of hardcoding hex values per status.
 */
export const STATUS_VISUALS: Record<EVMStatus, StatusVisual> = {
  UNDER_BUDGET: { color: "#15803d", background: "#dcfce7" },
  AHEAD_OF_SCHEDULE: { color: "#15803d", background: "#dcfce7" },
  ON_BUDGET: { color: "#1d4ed8", background: "#dbeafe" },
  ON_SCHEDULE: { color: "#1d4ed8", background: "#dbeafe" },
  AT_RISK: { color: "#b45309", background: "#fef3c7" },
  OVER_BUDGET: { color: "#b91c1c", background: "#fee2e2" },
  BEHIND_SCHEDULE: { color: "#b91c1c", background: "#fee2e2" },
  UNDEFINED: { color: "#374151", background: "#e5e7eb" },
};
