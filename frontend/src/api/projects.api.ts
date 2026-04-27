import { apiClient } from "./client";
import type { DataResponse, MessageResponse } from "@/types/api.types";
import type {
  ProjectCreatePayload,
  ProjectDetail,
  ProjectSummary,
  ProjectUpdatePayload,
} from "@/types/project.types";

export async function fetchProjects(): Promise<ProjectSummary[]> {
  const { data } = await apiClient.get<DataResponse<ProjectSummary[]>>("/projects");
  return data.data;
}

export async function fetchProjectById(projectId: string): Promise<ProjectDetail> {
  const { data } = await apiClient.get<DataResponse<ProjectDetail>>(
    `/projects/${projectId}`,
  );
  return data.data;
}

export async function createProject(
  payload: ProjectCreatePayload,
): Promise<ProjectSummary> {
  const { data } = await apiClient.post<DataResponse<ProjectSummary>>(
    "/projects",
    payload,
  );
  return data.data;
}

export async function updateProject(
  projectId: string,
  payload: ProjectUpdatePayload,
): Promise<ProjectSummary> {
  const { data } = await apiClient.put<DataResponse<ProjectSummary>>(
    `/projects/${projectId}`,
    payload,
  );
  return data.data;
}

export async function deleteProject(projectId: string): Promise<void> {
  await apiClient.delete<MessageResponse>(`/projects/${projectId}`);
}
