import { useContext } from "react";
import { useRecoilValue } from "recoil";

import { settingsState } from "chainlit/state/settings";

import { ChainlitContext } from "@chainlit/react-client";

interface Props {
  width?: number;
  style?: React.CSSProperties;
}

export const Logo = ({ style }: Props) => {
  const { theme } = useRecoilValue(settingsState);
  const apiClient = useContext(ChainlitContext);

  return (
    <img src={apiClient.getLogoEndpoint(theme)} alt="logo" style={style} />
  );
};
