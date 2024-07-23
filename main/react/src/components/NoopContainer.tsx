/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * This component does nothing, that is used to create dynamic component
 */

// ServerSideRendering を実行しないようにするためのコンポーネント

import { FC } from "react";

type Props = {
  children: any;
};

const NoopContainer: FC<Props> = ({ children }) => <>{children}</>;

export default NoopContainer;
