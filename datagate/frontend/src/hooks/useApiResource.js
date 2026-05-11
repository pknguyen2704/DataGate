import React from "react";

export function useApiResource(loader, deps = []) {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  const load = React.useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await loader();
      setData(res.data);
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }, deps);

  React.useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
