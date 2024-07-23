import { atom } from "recoil";

const getUserEnvFromLocalStorage = () => {
  if (typeof localStorage === "undefined") {
    return {};
  }
  const env = localStorage.getItem("userEnv");
  return env ? JSON.parse(env) : {};
};

export const userEnvState = atom<Record<string, string>>({
  key: "UserEnv",
  default: getUserEnvFromLocalStorage(),
});
