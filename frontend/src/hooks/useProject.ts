import { useCallback, useEffect, useState } from "react";

import { fetchProjectById } from "@/api/projects.api";
import { ApiError } from "@/api/client";
import type { ProjectDetail } from "@/types/project.types";

interface UseProjectState {
  project: ProjectDetail | null;
  loading: boolean;
  error: ApiError | null;
}

interface UseProjectResult extends UseProjectState {
  refetch: () => Promise<void>;
}

/**
 * Loads a project (with activities and EVM indicators) by id.
 * Re-exposes a `refetch` so consumers can refresh after mutations.
 */
export function useProject(projectId: string | undefined): UseProjectResult {
  const [state, setState] = useState<UseProjectState>({
    project: null,
    loading: true,
    error: null,
  });

  const load = useCallback(async () => {
    if (!projectId) {
      setState({ project: null, loading: false, error: null });
      return;
    }
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const project = await fetchProjectById(projectId);
      setState({ project, loading: false, error: null });
    } catch (err) {
      const error =
        err instanceof ApiError
          ? err
          : new ApiError("UNEXPECTED", String(err), 0);
      setState({ project: null, loading: false, error });
    }
  }, [projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  return { ...state, refetch: load };
}
