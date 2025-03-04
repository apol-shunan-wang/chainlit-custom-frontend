import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Stack from "@mui/material/Stack";

import { ITextElement } from "@chainlit/react-client";

import { TextElement } from "./Text";

interface Props {
  items: ITextElement[];
}

const InlinedTextList = ({ items }: Props) => (
  <Stack spacing={1}>
    {items.map((el, i) => {
      return (
        <Alert color="info" key={i} icon={false}>
          <AlertTitle>{el.name}</AlertTitle>
          <TextElement element={el} />
        </Alert>
      );
    })}
  </Stack>
);

export { InlinedTextList };
