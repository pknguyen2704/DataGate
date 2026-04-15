import React from "react";
import IncidentsPanel from "~/pages/Rules/Incidents/Incidents";

function Incidents({ assetDetail, assetObservability }) {
  return (
    <IncidentsPanel
      assetDetail={assetDetail}
      tableName={assetDetail?.table_name}
      initialIncidents={assetObservability?.incidents}
    />
  );
}

export default Incidents;
