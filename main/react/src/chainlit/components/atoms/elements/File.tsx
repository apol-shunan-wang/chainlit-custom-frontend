import Link from "@mui/material/Link";

import { Attachment } from "chainlit/components/atoms/Attachment";

import { type IFileElement } from "@chainlit/react-client";

const FileElement = ({ element }: { element: IFileElement }) => {
  if (!element.url) {
    return null;
  }

  return (
    <Link
      className={`${element.display}-file`}
      download={element.name}
      href={element.url}
      target="_blank"
      sx={{
        textDecoration: "none",
      }}
    >
      <Attachment name={element.name} mime={element.mime!} />
    </Link>
  );
};

export { FileElement };
