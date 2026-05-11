import React from "react";
import { Box, Button, Stack, Paper, Typography } from "@mui/material";
import { SettingsInputComponentOutlined, ModelTrainingOutlined, PeopleOutlined } from "@mui/icons-material";
import { Panel, TabContainer, TabButton } from "~/components/DataGate/Page";

// Import the sub-components
import PlatformConnection from "./PlatformConnection/PlatformConnection";
import ModelParameter from "./ModelParameter/ModelParameter";
import UserManagement from "./UserManagement/UserManagement";

function Settings() {
  const [tab, setTab] = React.useState("connections");

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        {/* Title Frame */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Settings</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Manage platform connections, AI models, and user access.</Typography>
          </Box>
        </Paper>

        <TabContainer>
          <TabButton 
            active={tab === "connections"}
            onClick={() => setTab("connections")}
            label="Platform Connection"
            icon={<SettingsInputComponentOutlined />}
          />
          <TabButton 
            active={tab === "model"}
            onClick={() => setTab("model")}
            label="Model Config"
            icon={<ModelTrainingOutlined />}
          />
          <TabButton 
            active={tab === "users"}
            onClick={() => setTab("users")}
            label="Users & RBAC"
            icon={<PeopleOutlined />}
          />
        </TabContainer>

        <Panel sx={{ flexGrow: 1 }}>
          <Box sx={{ minHeight: 400 }}>
            {tab === "connections" && <PlatformConnection />}
            {tab === "model" && <ModelParameter />}
            {tab === "users" && <UserManagement />}
          </Box>
        </Panel>
      </Stack>
    </Box>
  );
}

export default Settings;
