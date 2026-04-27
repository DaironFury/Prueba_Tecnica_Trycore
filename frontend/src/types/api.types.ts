/**
 * Generic envelope shared by every successful response from the backend.
 * The backend never returns bare arrays or scalars at the top level.
 */
export interface DataResponse<T> {
  data: T;
  message?: string;
}

export interface MessageResponse {
  message: string;
}

export interface ErrorDetail {
  code: string;
  message: string;
  field: string | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}
