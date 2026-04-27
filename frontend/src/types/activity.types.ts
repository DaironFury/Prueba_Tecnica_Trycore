import type { EVMIndicators } from "./evm.types";

export interface Activity {
  id: string;
  project_id: string;
  name: string;
  bac: number;
  planned_percent: number;
  actual_percent: number;
  actual_cost: number;
  indicators: EVMIndicators;
  created_at: string;
  updated_at: string;
}

export interface ActivityCreatePayload {
  name: string;
  bac: number;
  planned_percent: number;
  actual_percent: number;
  actual_cost: number;
}

export type ActivityUpdatePayload = Partial<ActivityCreatePayload>;
