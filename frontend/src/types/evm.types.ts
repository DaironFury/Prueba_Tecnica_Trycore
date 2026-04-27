/**
 * Status codes mirror the strings emitted by the backend's interpretation
 * functions. Using a discriminated union prevents typos at the call site.
 */
export type CPIStatus =
  | "UNDER_BUDGET"
  | "ON_BUDGET"
  | "AT_RISK"
  | "OVER_BUDGET"
  | "UNDEFINED";

export type SPIStatus =
  | "AHEAD_OF_SCHEDULE"
  | "ON_SCHEDULE"
  | "AT_RISK"
  | "BEHIND_SCHEDULE"
  | "UNDEFINED";

export type EVMStatus = CPIStatus | SPIStatus;

export interface EVMIndicators {
  bac: number;
  pv: number;
  ev: number;
  ac: number;
  cv: number;
  sv: number;
  cpi: number | null;
  spi: number | null;
  eac: number | null;
  vac: number | null;
  cpi_status: CPIStatus;
  spi_status: SPIStatus;
  cpi_label: string;
  spi_label: string;
}
