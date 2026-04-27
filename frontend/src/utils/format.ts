const CURRENCY_FORMATTER = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0,
});

const RATIO_FORMATTER = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const PERCENT_FORMATTER = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const NULL_PLACEHOLDER = "N/A";

export function formatCurrency(value: number | null): string {
  if (value === null || Number.isNaN(value)) return NULL_PLACEHOLDER;
  return CURRENCY_FORMATTER.format(value);
}

export function formatRatio(value: number | null): string {
  if (value === null || Number.isNaN(value)) return NULL_PLACEHOLDER;
  return RATIO_FORMATTER.format(value);
}

export function formatPercent(value: number | null): string {
  if (value === null || Number.isNaN(value)) return NULL_PLACEHOLDER;
  return `${PERCENT_FORMATTER.format(value)}%`;
}
