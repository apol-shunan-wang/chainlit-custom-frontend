import { atom } from "recoil";

type ThemeVariant = "dark" | "light";

const getThemeFormLocalStorage = () => {
  let defaultTheme = "light" as ThemeVariant;

  if (typeof window === "undefined" || typeof localStorage === "undefined") {
    return defaultTheme;
  }

  defaultTheme = (window.theme?.default || "dark") as ThemeVariant;

  const preferredTheme = localStorage.getItem(
    "themeVariant"
  ) as ThemeVariant | null;

  return preferredTheme ? preferredTheme : defaultTheme;
};

export const defaultSettingsState = {
  open: false,
  defaultCollapseContent: true,
  isChatHistoryOpen: true,
  language: "en-US",
  theme: getThemeFormLocalStorage(),
};

export const settingsState = atom<{
  open: boolean;
  theme: ThemeVariant;
  isChatHistoryOpen: boolean;
  language: string;
}>({
  key: "AppSettings",
  default: defaultSettingsState,
});
