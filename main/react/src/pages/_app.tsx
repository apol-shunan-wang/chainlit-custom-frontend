import { AppProps } from "next/app";
import dynamic from "next/dynamic";
import { useRouter } from "next/router";
import { Session } from "next-auth";
import { RecoilRoot } from "recoil";
import { ChainlitContext } from "@chainlit/react-client";
import { apiClient } from "chainlit/api";
import ChainlitWrapper from "@/chainlit/ChainlitWrapper";

// Children of this component will not be rendered in server side
// https://ryotarch.com/javascript/react/next-js-with-csr/
const DynamicContainer = dynamic(() => import("../components/NoopContainer"), {
  ssr: false,
});

// react router の ready の状態を回避するため
type RouterWrapperProps = {
  children: React.ReactNode;
};
const RouterWrapper = (props: RouterWrapperProps): JSX.Element => {
  const { children } = props;
  const router = useRouter();

  if (!router.isReady) {
    throw new Promise(() => {});
  }
  return <>{children}</>;
};

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////
// APP
export default function MyApp({
  Component,
  pageProps: { session, ...pageProps },
}: AppProps<{ session: Session }>): JSX.Element {
  const router = useRouter();

  return (
    <DynamicContainer>
      <RecoilRoot>
        <RouterWrapper>
          {router.pathname.includes("chainlit") ? (
            <ChainlitWrapper />
          ) : (
            <Component {...pageProps} />
          )}
        </RouterWrapper>
      </RecoilRoot>
    </DynamicContainer>
  );
}
