import React, { useMemo } from "react";
import { Navigate, useLocation } from "react-router-dom";

const Rules = () => {
  const location = useLocation();
  const redirectTarget = useMemo(() => {
    const params = new URLSearchParams(location.search);
    params.set("section", "observability");
    params.set("obsTab", params.get("tab") === "incidents" ? "incidents" : "rules");
    params.delete("tab");
    return `/explore?${params.toString()}`;
  }, [location.search]);

  return <Navigate replace to={redirectTarget} />;
};

export default Rules;
