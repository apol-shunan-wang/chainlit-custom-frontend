import ArrowBack from "@mui/icons-material/ArrowBack";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { useLayoutMaxWidth } from "chainlit/hooks/useLayoutMaxWidth";

import { IMessageElement } from "@chainlit/react-client";

import { Element } from "./Element";

interface ElementViewProps {
  element: IMessageElement;
  onGoBack?: () => void;
}

const ElementView = ({ element, onGoBack }: ElementViewProps) => {
  const layoutMaxWidth = useLayoutMaxWidth();

  return (
    <Box
      display="flex"
      flexDirection="column"
      flexGrow={1}
      p={3}
      gap={2}
      boxSizing="border-box"
      mx="auto"
      sx={{
        width: "100%",
        maxWidth: layoutMaxWidth,
        color: "text.primary"
      }}
      id="element-view"
    >
      <Stack direction="row" gap={1}>
        {onGoBack ? (
          <IconButton edge="start" onClick={onGoBack}>
            <ArrowBack />
          </IconButton>
        ) : null}
        <Typography fontWeight={700} fontSize="25px">
          {element.name}
        </Typography>
      </Stack>

      <Element element={element} />
    </Box>
  );
};

export { ElementView, Element };
