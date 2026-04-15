import React from "react";
import RulesList from "~/pages/Rules/RulesList/RulesList";

function RulesManagement({ assetDetail }) {
  return <RulesList assetDetail={assetDetail} tableName={assetDetail?.table_name} />;
}

export default RulesManagement;
