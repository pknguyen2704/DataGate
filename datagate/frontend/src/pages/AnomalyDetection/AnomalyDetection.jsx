import React, { useMemo } from "react";
import { Navigate, useLocation } from "react-router-dom";

const AnomalyDetection = () => {
  const location = useLocation();
  const redirectTarget = useMemo(() => {
    const params = new URLSearchParams(location.search);
    params.set("section", "observability");
    params.set("obsTab", "anomaly");
    return `/explore?${params.toString()}`;
  }, [location.search]);

  return <Navigate replace to={redirectTarget} />;
};

export default AnomalyDetection;
