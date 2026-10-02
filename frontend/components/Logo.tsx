"use client";

export default function Logo({ size = 40, clickable = false }: { size?: number; clickable?: boolean }) {
  const svg = (
    <svg width={size} height={size} viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="brandGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#ff6d00" />
          <stop offset="50%" stopColor="#5a189a" />
          <stop offset="100%" stopColor="#9d4edd" />
        </linearGradient>
        <linearGradient id="shine" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d="M32 2 L58 17 L58 47 L32 62 L6 47 L6 17 Z" fill="url(#brandGrad)" />
      <path d="M32 2 L58 17 L32 32 L6 17 Z" fill="url(#shine)" />
      <text x="32" y="43" textAnchor="middle" fontSize="30" fontWeight="900" fill="#ffffff" fontFamily="system-ui,sans-serif">T</text>
      <circle cx="49" cy="14" r="3.5" fill="#ffffff" />
    </svg>
  );

  if (!clickable) return svg;

  return (
    <button
      onClick={() => window.location.reload()}
      className="hover:opacity-80 active:scale-95 transition cursor-pointer"
      title="Refresh page"
      aria-label="Refresh page"
    >
      {svg}
    </button>
  );
}
