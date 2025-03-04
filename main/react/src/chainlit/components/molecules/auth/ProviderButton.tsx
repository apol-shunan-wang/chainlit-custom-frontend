import { grey } from "chainlit/theme/palette";

import GitHub from "@mui/icons-material/GitHub";
import Google from "@mui/icons-material/Google";
import Microsoft from "@mui/icons-material/Microsoft";
import Button from "@mui/material/Button";

import { Auth0 } from "chainlit/components/atoms/icons/Auth0";
import { Cognito } from "chainlit/components/atoms/icons/Cognito";
import { Descope } from "chainlit/components/atoms/icons/Descope";
import { Gitlab } from "chainlit/components/atoms/icons/Gitlab";
import { Okta } from "chainlit/components/atoms/icons/Okta";
import { useTranslation } from "chainlit/components/i18n/Translator";

function capitalizeFirstLetter(string: string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function getProviderName(provider: string) {
  switch (provider) {
    case "azure-ad":
    case "azure-ad-hybrid":
      return "Microsoft";
    case "github":
      return "GitHub";
    case "okta":
      return "Okta";
    case "descope":
      return "Descope";
    case "aws-cognito":
      return "Cognito";
    default:
      return capitalizeFirstLetter(provider);
  }
}

function renderProviderIcon(provider: string) {
  switch (provider) {
    case "google":
      return <Google />;
    case "github":
      return <GitHub />;
    case "azure-ad":
    case "azure-ad-hybrid":
      return <Microsoft />;
    case "okta":
      return <Okta />;
    case "auth0":
      return <Auth0 />;
    case "descope":
      return <Descope />;
    case "aws-cognito":
      return <Cognito />;
    case "gitlab":
      return <Gitlab />;
    default:
      return null;
  }
}

interface ProviderButtonProps {
  provider: string;
  onClick: () => void;
  isSignIn?: boolean;
}

const ProviderButton = ({
  provider,
  onClick,
  isSignIn
}: ProviderButtonProps): JSX.Element => {
  const { t } = useTranslation();
  return (
    <Button
      variant="outlined"
      color="inherit"
      startIcon={renderProviderIcon(provider.toLowerCase())}
      onClick={onClick}
      sx={{
        width: "100%",
        textTransform: "none",
        borderColor: grey[400],
        padding: 1.5,
        paddingLeft: 3,
        justifyContent: "flex-start"
      }}
    >
      {isSignIn
        ? t("components.molecules.auth.providerButton.continue", {
            provider: getProviderName(provider)
          })
        : t("components.molecules.auth.providerButton.signup", {
            provider: getProviderName(provider)
          })}
    </Button>
  );
};

export { ProviderButton };
