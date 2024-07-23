import { useTheme } from "@mui/material/styles";

const useIsDarkMode = (): boolean => {
  const theme = useTheme();

  return theme.palette.mode === "dark";
};

export { useIsDarkMode };
