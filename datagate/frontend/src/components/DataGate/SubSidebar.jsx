import React, { useState, useEffect } from "react";
import { 
  Box, Typography, Paper, List, ListItemButton, ListItemText, 
  Collapse, CircularProgress 
} from "@mui/material";
import { ExpandLess, ExpandMore } from "@mui/icons-material";

export const SubSidebar = ({ 
  tree, 
  selectedTableId, 
  onTableSelect, 
  title = "Data Sources",
  sx = {}
}) => {
  const [openSchemas, setOpenSchemas] = useState({});

  const toggleSchema = (schema) => {
    setOpenSchemas(prev => ({ ...prev, [schema]: !prev[schema] }));
  };

  useEffect(() => {
    if (tree.data && tree.data.length > 0 && !selectedTableId) {
      const firstSchema = tree.data.find(s => s.tables.length > 0) || tree.data[0];
      setOpenSchemas({ [firstSchema.schema_name]: true });
      if (firstSchema.tables.length > 0) {
        onTableSelect(firstSchema.tables[0].table_id, `${firstSchema.schema_name}.${firstSchema.tables[0].table_name}`);
      }
    }
  }, [tree.data]);

  return (
    <Paper 
      variant="outlined" 
      sx={{ 
        height: 'auto', 
        overflow: 'hidden', 
        borderRadius: 2, 
        bgcolor: 'white',
        border: '1px solid',
        borderColor: 'divider',
        ...sx 
      }}
    >
      <Box sx={{ p: 2.5, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="subtitle1" fontWeight="bold">{title}</Typography>
      </Box>
      {tree.loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24}/></Box>
      ) : (
        <List component="nav" disablePadding sx={{ py: 1 }}>
          {(tree.data || []).map((schema) => (
            <React.Fragment key={schema.schema_name}>
              <ListItemButton 
                onClick={() => toggleSchema(schema.schema_name)} 
                sx={{ 
                  py: 1.5,
                  px: 2,
                  bgcolor: 'transparent',
                  '&:hover': { bgcolor: 'rgba(0,0,0,0.02)' }
                }}
              >
                <ListItemText 
                  primary={schema.schema_name} 
                  primaryTypographyProps={{ fontWeight: 800, fontSize: '0.85rem', color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 0.5 }} 
                />
                {openSchemas[schema.schema_name] ? <ExpandLess fontSize="small" sx={{ opacity: 0.5 }} /> : <ExpandMore fontSize="small" sx={{ opacity: 0.5 }} />}
              </ListItemButton>
              <Collapse in={openSchemas[schema.schema_name]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding sx={{ pb: 1 }}>
                  {schema.tables.map((table) => {
                    const active = selectedTableId === table.table_id;
                    return (
                      <ListItemButton 
                        key={table.table_id} 
                        sx={{ 
                          pl: 4, 
                          py: 1,
                          mr: 1.5,
                          ml: 1.5,
                          my: 0.2,
                          borderRadius: '8px',
                          bgcolor: active ? 'primary.main' : 'transparent',
                          color: active ? 'white' : 'text.primary',
                          '&:hover': { 
                            bgcolor: active ? 'primary.dark' : 'primary.50',
                            color: active ? 'white' : 'primary.main'
                          },
                          transition: 'all 0.2s'
                        }}
                        selected={active}
                        onClick={() => onTableSelect(table.table_id, `${schema.schema_name}.${table.table_name}`)}
                      >
                        <ListItemText 
                          primary={table.table_name} 
                          primaryTypographyProps={{ 
                            fontSize: '0.875rem', 
                            fontWeight: active ? 700 : 500 
                          }} 
                        />
                      </ListItemButton>
                    );
                  })}
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};
