import {
  darkGreyButtonTheme,
  lightGreyButtonTheme
} from "chainlit/theme/theme";

import Button, { ButtonProps } from "@mui/material/Button";
import { ThemeProvider } from "@mui/material/styles";
import { useTheme } from "@mui/material/styles";

const GreyButton = ({ sx, ...props }: ButtonProps) => {
  const theme = useTheme();
  const greyTheme =
    theme.palette.mode === "dark" ? darkGreyButtonTheme : lightGreyButtonTheme;

  return (
    <ThemeProvider theme={greyTheme}>
      <Button
        {...props}
        disableElevation
        disableRipple
        sx={{
          ...sx,
          textTransform: "none"
        }}
      />
    </ThemeProvider>
  );
};

export { GreyButton };
