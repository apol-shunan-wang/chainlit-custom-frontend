import React, { useEffect } from "react";
import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import { useRecoilValue } from "recoil";
import { Toaster } from "sonner";
import { makeTheme } from "chainlit/theme";

import { Box, GlobalStyles } from "@mui/material";
import { Theme, ThemeProvider } from "@mui/material/styles";

import { useAuth, useChatSession, useConfig } from "@chainlit/react-client";

import ChatSettingsModal from "chainlit/components/organisms/chat/settings";

import { settingsState } from "chainlit/state/settings";
import { userEnvState } from "chainlit/state/user";

import "./App.module.css";

import getRouterBasename from "chainlit/utils/router";

import AuthCallback from "chainlit/pages/AuthCallback";
import Element from "chainlit/pages/Element";
import Env from "chainlit/pages/Env";
import Home from "chainlit/pages/Home";
import Login from "chainlit/pages/Login";
import Thread from "chainlit/pages/Thread";

type Primary = {
  dark?: string;
  light?: string;
  main?: string;
};

type Text = {
  primary?: string;
  secondary?: string;
};

type ThemOverride = {
  primary?: Primary;
  background?: string;
  paper?: string;
  text?: Text;
};

declare global {
  interface Window {
    theme?: {
      default: string;
      light?: ThemOverride;
      dark?: ThemOverride;
    };
  }
}

export function overrideTheme(theme: Theme) {
  const variant = theme.palette.mode;
  const variantOverride = window?.theme?.[variant] as ThemOverride;
  if (variantOverride?.background) {
    theme.palette.background.default = variantOverride.background;
  }
  if (variantOverride?.paper) {
    theme.palette.background.paper = variantOverride.paper;
  }
  if (variantOverride?.primary?.main) {
    theme.palette.primary.main = variantOverride.primary.main;
  }
  if (variantOverride?.primary?.dark) {
    theme.palette.primary.dark = variantOverride.primary.dark;
  }
  if (variantOverride?.primary?.light) {
    theme.palette.primary.light = variantOverride.primary.light;
  }
  if (variantOverride?.text?.primary) {
    theme.palette.text.primary = variantOverride.text.primary;
  }
  if (variantOverride?.text?.secondary) {
    theme.palette.text.secondary = variantOverride.text.secondary;
  }

  return theme;
}

function App() {
  const { theme: themeVariant } = useRecoilValue(settingsState);
  const { config } = useConfig();

  // @ts-expect-error custom property
  const fontFamily = window.theme?.font_family;
  const theme = overrideTheme(makeTheme(themeVariant, fontFamily));
  const { isAuthenticated, accessToken } = useAuth();
  const userEnv = useRecoilValue(userEnvState);
  const { connect, chatProfile, setChatProfile } = useChatSession();

  const router = createBrowserRouter(
    [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "/env",
        element: <Env />,
      },
      {
        path: "/thread/:id?",
        element: <Thread />,
      },
      {
        path: "/element/:id",
        element: <Element />,
      },
      {
        path: "/login",
        element: <Login />,
      },
      {
        path: "/login/callback",
        element: <AuthCallback />,
      },
      {
        path: "*",
        element: <Navigate replace to="/" />,
      },
    ],
    { basename: getRouterBasename() }
  );

  const configLoaded = !!config;

  const chatProfileOk = configLoaded
    ? config.chatProfiles.length
      ? !!chatProfile
      : true
    : false;

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    } else if (!chatProfileOk) {
      return;
    } else {
      connect({
        userEnv,
        accessToken,
      });
    }
  }, [userEnv, accessToken, isAuthenticated, connect, chatProfileOk]);

  if (configLoaded && config.chatProfiles.length && !chatProfile) {
    // Autoselect the first default chat profile
    const defaultChatProfile = config.chatProfiles.find(
      (profile) => profile.default
    );
    if (defaultChatProfile) {
      setChatProfile(defaultChatProfile.name);
    } else {
      setChatProfile(config.chatProfiles[0].name);
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles
        styles={{
          body: { backgroundColor: theme.palette.background.default },
        }}
      />
      <Toaster
        className="toast"
        position="top-right"
        toastOptions={{
          style: {
            fontFamily: theme.typography.fontFamily,
            background: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            color: theme.palette.text.primary,
          },
        }}
      />
      <Box
        display="flex"
        height="100vh"
        maxHeight="-webkit-fill-available"
        width="100vw"
        sx={{ overflowX: "hidden" }}
      >
        <ChatSettingsModal />
        <RouterProvider router={router} />
      </Box>
    </ThemeProvider>
  );
}

export default App;
