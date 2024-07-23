import { useRecoilValue } from "recoil";

import { Stack, Typography } from "@mui/material";

import { Translator } from "chainlit/components/i18n";

import "chainlit/assets/logo_dark.svg";
import LogoDark from "chainlit/assets/logo_dark.svg";
import "chainlit/assets/logo_light.svg";
import LogoLight from "chainlit/assets/logo_light.svg";

import { settingsState } from "chainlit/state/settings";

export default function WaterMark() {
  const { theme } = useRecoilValue(settingsState);
  const Logo = theme === "light" ? LogoLight : LogoDark;
  return (
    <Stack mx="auto" className="watermark">
      <a
        href="https://github.com/Chainlit/chainlit"
        target="_blank"
        style={{
          display: "flex",
          alignItems: "center",
          textDecoration: "none",
        }}
      >
        <Typography fontSize="12px" color="text.secondary">
          <Translator path="components.organisms.chat.inputBox.waterMark.text" />
        </Typography>
        <Logo
          style={{
            width: 65,
            height: "auto",
            filter: "grayscale(1)",
            marginLeft: "4px",
          }}
        />
      </a>
    </Stack>
  );
}
