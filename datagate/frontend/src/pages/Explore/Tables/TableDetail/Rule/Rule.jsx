import React from "react";
import {
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import {
  FactCheckOutlined as VerificationIcon,
  RuleOutlined as RuleIcon,
} from "@mui/icons-material";
import { datagateColors, panelSx } from "~/theme";
import RuleManagement from "./RuleManagement/RuleManagement";
import RuleVerification from "./RuleVerification/RuleVerification";

const RULE_SECTIONS = {
  management: 0,
  verification: 1,
};

function RulesPanel({ tableId, columns = [] }) {
  const [section, setSection] = React.useState("management");

  return (
    <Stack spacing={3}>
      <Paper
        sx={{
          ...panelSx,
          p: 3,
          background:
            "linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(255, 255, 255, 0.94) 58%, rgba(248, 250, 252, 1) 100%)",
        }}
      >
        <Stack spacing={1.5}>
          <Typography variant="h5" fontWeight={800}>
            Rule Center
          </Typography>
          <Typography color="text.secondary">
            Review top suggested rules for this table, activate approved rules, and inspect verification outcomes across batches.
          </Typography>
        </Stack>
      </Paper>

      <Paper sx={{ ...panelSx, p: 1, borderColor: datagateColors.cardBorder }}>
        <Tabs
          value={RULE_SECTIONS[section]}
          onChange={(_, nextTab) => {
            const nextSection = Object.keys(RULE_SECTIONS).find((key) => RULE_SECTIONS[key] === nextTab) || "management";
            setSection(nextSection);
          }}
        >
          <Tab icon={<RuleIcon fontSize="small" />} iconPosition="start" label="Rule Management" />
          <Tab icon={<VerificationIcon fontSize="small" />} iconPosition="start" label="Rule Verification" />
        </Tabs>
      </Paper>

      {section === "management" ? <RuleManagement tableId={tableId} columns={columns} /> : null}
      {section === "verification" ? <RuleVerification tableId={tableId} /> : null}
    </Stack>
  );
}

export default RulesPanel;
