import { toast } from "sonner";

import { ChainlitAPI, ClientError } from "@chainlit/react-client";

const devServer = "http://localhost:8000/chainlit";
const url = devServer;

const serverUrl = new URL(url);

const httpEndpoint = serverUrl.toString();

const on401 = () => {};

const onError = (error: ClientError) => {
  toast.error(error.toString());
};

export const apiClient = new ChainlitAPI(
  httpEndpoint,
  "webapp",
  on401,
  onError
);
