import { useSearchParams } from "next/navigation";
import { useMemo } from "react";

export function useQuery() {
  const search = useSearchParams();

  return useMemo(() => new URLSearchParams(search), [search]);
}
