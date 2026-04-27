import { apiClient } from "./client";
import type {
  Activity,
  ActivityCreatePayload,
  ActivityUpdatePayload,
} from "@/types/activity.types";
import type { DataResponse, MessageResponse } from "@/types/api.types";

export async function createActivity(
  projectId: string,
  payload: ActivityCreatePayload,
): Promise<Activity> {
  const { data } = await apiClient.post<DataResponse<Activity>>(
    `/projects/${projectId}/activities`,
    payload,
  );
  return data.data;
}

export async function updateActivity(
  projectId: string,
  activityId: string,
  payload: ActivityUpdatePayload,
): Promise<Activity> {
  const { data } = await apiClient.put<DataResponse<Activity>>(
    `/projects/${projectId}/activities/${activityId}`,
    payload,
  );
  return data.data;
}

export async function deleteActivity(
  projectId: string,
  activityId: string,
): Promise<void> {
  await apiClient.delete<MessageResponse>(
    `/projects/${projectId}/activities/${activityId}`,
  );
}
