import App from "chainlit/App";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";

import { useApi, useAuth, useConfig } from "@chainlit/react-client";
import { useRouter } from "next/router";

export default function AppWrapper() {
  const { isAuthenticated, isReady } = useAuth();
  const { language: languageInUse } = useConfig();
  const { i18n } = useTranslation();
  const router = useRouter();

  function handleChangeLanguage(languageBundle: any): void {
    i18n.addResourceBundle(languageInUse, "translation", languageBundle);
    i18n.changeLanguage(languageInUse);
  }

  const { data: translations } = useApi<any>(
    `/project/translations?language=${languageInUse}`
  );

  if (
    isReady &&
    !isAuthenticated &&
    !router.pathname.includes("chainlit/login") &&
    !router.pathname.includes("chainlit/login/callback")
  ) {
    router.push("/chainlit/login");
  }

  useEffect(() => {
    if (!translations) return;
    handleChangeLanguage(translations.translation);
  }, [translations]);

  if (!isReady) {
    return null;
  }

  return <App />;
}
