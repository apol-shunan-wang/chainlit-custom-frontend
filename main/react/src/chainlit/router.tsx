import { Navigate, createBrowserRouter } from "react-router-dom";
import getRouterBasename from "chainlit/utils/router";

import AuthCallback from "chainlit/pages/AuthCallback";
import Element from "chainlit/pages/Element";
import Env from "chainlit/pages/Env";
import Home from "chainlit/pages/Home";
import Login from "chainlit/pages/Login";
import Thread from "chainlit/pages/Thread";

export const router = () =>
  createBrowserRouter(
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
