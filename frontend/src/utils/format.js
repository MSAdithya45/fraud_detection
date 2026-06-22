export const formatNumber = (n) =>
  new Intl.NumberFormat("en-US").format(Math.round(n ?? 0));

export const formatCurrency = (n, currency = "USD") =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(n ?? 0);

export const formatPercent = (n, digits = 1) => `${(n ?? 0).toFixed(digits)}%`;

export const timeAgo = (date) => {
  const d = typeof date === "string" ? new Date(date) : date;
  const seconds = Math.floor((Date.now() - d.getTime()) / 1000);
  const ranges = [
    ["year", 31536000],
    ["month", 2592000],
    ["day", 86400],
    ["hour", 3600],
    ["min", 60],
    ["sec", 1],
  ];
  for (const [label, secs] of ranges) {
    const value = Math.floor(seconds / secs);
    if (value >= 1) return `${value} ${label}${value > 1 ? "s" : ""} ago`;
  }
  return "just now";
};

export const riskFromProbability = (p) => {
  if (p >= 0.7) return "High";
  if (p >= 0.4) return "Medium";
  return "Low";
};
