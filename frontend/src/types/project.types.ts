import type { Activity } from "./activity.types";
import type { EVMIndicators } from "./evm.types";

export interface ProjectSummary {
  id: string;
  name: string;
  description: string | null;
  status_date: string;
  activity_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail {
  id: string;
  name: string;
  description: string | null;
  status_date: string;
  indicators: EVMIndicators;
  activities: Activity[];
  created_at: string;
  updated_at: string;
}

export interface ProjectCreatePayload {
  name: string;
  description?: string;
  status_date: string;
}

export type ProjectUpdatePayload = Partial<ProjectCreatePayload>;
