import AppWrapper from "chainlit/AppWrapper";
import { apiClient } from "chainlit/api";
import React from "react";

import { i18nSetupLocalization } from "./i18n";
import { ChainlitContext } from "@chainlit/react-client";

i18nSetupLocalization();

export default function ChainlitWrapper() {
  return (
    <ChainlitContext.Provider value={apiClient}>
      <AppWrapper />
    </ChainlitContext.Provider>
  );
}
