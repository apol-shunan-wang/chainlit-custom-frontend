import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Logo } from "chainlit/components/atoms/logo";
import { Translator } from "chainlit/components/i18n";
import { AuthLogin } from "chainlit/components/molecules/auth";

import { useQuery } from "chainlit/hooks/query";

import { ChainlitContext, useAuth } from "@chainlit/react-client";

export default function Login() {
  const query = useQuery();
  const { data: config, setAccessToken, user } = useAuth();
  const [error, setError] = useState("");
  const apiClient = useContext(ChainlitContext);

  const navigate = useNavigate();

  const handleHeaderAuth = async () => {
    try {
      const json = await apiClient.headerAuth();
      setAccessToken(json.access_token);
      navigate("/");
    } catch (error) {
      setError(error.message);
    }
  };

  const handlePasswordLogin = async (
    email: string,
    password: string,
    callbackUrl: string
  ) => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    try {
      const json = await apiClient.passwordAuth(formData);
      setAccessToken(json.access_token);
      navigate(callbackUrl);
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    setError(query.get("error") || "");
  }, [query]);

  useEffect(() => {
    if (!config) {
      return;
    }
    if (!config.requireLogin) {
      navigate("/");
    }
    if (config.headerAuth) {
      handleHeaderAuth();
    }
    if (user) {
      navigate("/");
    }
  }, [config, user]);

  return (
    <AuthLogin
      title={<Translator path="components.molecules.auth.authLogin.title" />}
      error={error}
      callbackUrl="/"
      providers={config?.oauthProviders || []}
      onPasswordSignIn={config?.passwordAuth ? handlePasswordLogin : undefined}
      onOAuthSignIn={async (provider: string) => {
        window.location.href = apiClient.getOAuthEndpoint(provider);
      }}
      renderLogo={<Logo style={{ maxWidth: "60%", maxHeight: "90px" }} />}
    />
  );
}
