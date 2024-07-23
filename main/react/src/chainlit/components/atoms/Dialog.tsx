import { ReactNode } from "react";

import { Box } from "@mui/material";
import { Dialog as MDialog, DialogProps as MDialogProps } from "@mui/material";
import { DialogActions } from "@mui/material";
import { DialogContent } from "@mui/material";
import { DialogTitle } from "@mui/material";
import { grey } from "@mui/material/colors";

type DialogProps = {
  actions?: ReactNode;
  content?: ReactNode;
  title?: ReactNode;
} & Omit<MDialogProps, "content" | "title">;

export const Dialog = ({ actions, content, title, ...rest }: DialogProps) => {
  return (
    <MDialog
      {...rest}
      fullWidth
      sx={{
        border: theme =>
          theme.palette.mode === "dark" ? `1px solid ${grey[800]}` : null,
        borderRadius: 1
      }}
    >
      <Box bgcolor="background.paper">
        {title ? (
          <DialogTitle>
            <>{title}</>
          </DialogTitle>
        ) : null}

        {content ? <DialogContent>{content}</DialogContent> : null}

        {actions ? (
          <DialogActions sx={{ padding: theme => theme.spacing(0, 3, 2) }}>
            <>{actions}</>
          </DialogActions>
        ) : null}
      </Box>
    </MDialog>
  );
};
