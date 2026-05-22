import React from "react";
import { Box, Tab, Tabs, Typography } from "@mui/material";
import TuneOutlined from "@mui/icons-material/TuneOutlined";
import SettingsSuggestOutlined from "@mui/icons-material/SettingsSuggestOutlined";
import ModelParameter from "./ModelParameter/ModelParameter";
import Config from "./Config/Config";

function AnomalyConfig() {
  const [tab, setTab] = React.useState(0);

  return (
    <Box>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(event, value) => setTab(value)}
        >
          <Tab icon={<TuneOutlined fontSize="small" />} iconPosition="start" label="Parameter" />
          <Tab icon={<SettingsSuggestOutlined fontSize="small" />} iconPosition="start" label="Config" />
        </Tabs>
      </Box>
      {tab === 0 && <ModelParameter />}
      {tab === 1 && <Config />}
    </Box>
  );
}

export default AnomalyConfig;
