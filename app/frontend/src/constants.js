export const CATEGORY_OPTIONS = [
  {
    value: "cleanser",
    title: "Cleanser",
    copy: "Fresh, light blue energy",
  },
  {
    value: "treatment",
    title: "Treatment",
    copy: "Targeted care with a bright finish",
  },
  {
    value: "moisturizer",
    title: "Moisturizer",
    copy: "Soft comfort and warm hydration",
  },
];

export const CONCERN_OPTIONS = [
  { value: "acne", label: "Acne" },
  { value: "redness", label: "Redness" },
  { value: "texture", label: "Texture" },
  { value: "dryness", label: "Dryness" },
  { value: "oily", label: "Oily" },
  { value: "dark-spots", label: "Dark spots" },
];

export const SKIN_TYPE_OPTIONS = [
  { value: "oily", label: "Oily" },
  { value: "dry", label: "Dry" },
  { value: "combination", label: "Combination" },
  { value: "sensitive", label: "Sensitive" },
];

export const THEME_CONFIG = {
  default: {
    accent: "#ef9bb0",
    accentStrong: "#de6d8a",
    accentSoft: "rgba(239, 155, 176, 0.18)",
    glow: "rgba(239, 155, 176, 0.32)",
    bgTop: "#fff7fb",
    bgBottom: "#f7f4ef",
    label: "Fresh skincare match",
    reviewLabel: "Community powered",
  },
  cleanser: {
    accent: "#92cde3",
    accentStrong: "#5caecf",
    accentSoft: "rgba(146, 205, 227, 0.2)",
    glow: "rgba(146, 205, 227, 0.35)",
    bgTop: "#f7fcff",
    bgBottom: "#eef7fb",
    label: "Fresh cleanser flow",
    reviewLabel: "Fresh cleanser feedback",
  },
  treatment: {
    accent: "#f2cf73",
    accentStrong: "#e0af35",
    accentSoft: "rgba(242, 207, 115, 0.24)",
    glow: "rgba(242, 207, 115, 0.34)",
    bgTop: "#fffdf2",
    bgBottom: "#f8f2dc",
    label: "Bright treatment flow",
    reviewLabel: "Targeted treatment feedback",
  },
  moisturizer: {
    accent: "#dcc0a4",
    accentStrong: "#c7a37f",
    accentSoft: "rgba(220, 192, 164, 0.2)",
    glow: "rgba(220, 192, 164, 0.3)",
    bgTop: "#fffaf3",
    bgBottom: "#f6efe7",
    label: "Soft hydration flow",
    reviewLabel: "Comfort-first moisturizer feedback",
  },
  sunscreen: {
    accent: "#f2cf73",
    accentStrong: "#e0af35",
    accentSoft: "rgba(242, 207, 115, 0.24)",
    glow: "rgba(242, 207, 115, 0.34)",
    bgTop: "#fffdf2",
    bgBottom: "#f8f2dc",
    label: "Bright sunscreen flow",
    reviewLabel: "Sun-care community notes",
  },
};
