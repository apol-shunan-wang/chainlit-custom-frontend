import hljs from "highlight.js";
import { useEffect, useRef } from "react";
import { grey } from "chainlit/theme/palette";

import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { ClipboardCopy } from "chainlit/components/atoms/ClipboardCopy";

import { useIsDarkMode } from "chainlit/hooks/useIsDarkMode";

import "highlight.js/styles/monokai-sublime.css";

const CodeSnippet = ({
  language,
  children
}: {
  language: string;
  children: string;
}) => {
  const codeRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (codeRef.current) {
      const highlighted =
        codeRef.current.getAttribute("data-highlighted") === "yes";
      if (!highlighted) {
        hljs.highlightElement(codeRef.current);
      }
    }
  }, []);

  return (
    <pre style={{ margin: 0 }}>
      <code
        ref={codeRef}
        style={{
          borderBottomLeftRadius: "0.7rem",
          borderBottomRightRadius: "0.7rem",
          fontFamily: "monospace",
          fontSize: "14px"
        }}
        className={`language-${language}`}
      >
        {children}
      </code>
    </pre>
  );
};

const Code = ({ children, ...props }: any) => {
  const isDarkMode = useIsDarkMode();
  const codeChildren = props.node?.children?.[0];
  const className = codeChildren?.properties?.className?.[0];
  const match = /language-(\w+)/.exec(className || "");
  const code = codeChildren?.children?.[0]?.value;

  const showSyntaxHighlighter = match && code;

  const highlightedCode = showSyntaxHighlighter ? (
    <CodeSnippet language={match[1]}>{code}</CodeSnippet>
  ) : null;

  const nonHighlightedCode = showSyntaxHighlighter ? null : (
    <Box
      sx={{
        background: isDarkMode ? grey[900] : grey[200],
        borderRadius: "0.7rem",
        padding: theme => theme.spacing(1),
        paddingRight: "2.5em",
        minHeight: "20px",
        overflowX: "auto"
      }}
    >
      <code
        {...props}
        style={{
          whiteSpace: "pre-wrap"
        }}
      >
        {children}
      </code>
    </Box>
  );

  return (
    <Box
      sx={{
        position: "relative"
      }}
    >
      <Stack
        px={2}
        py={1}
        direction="row"
        sx={{
          justifyContent: "space-between",
          alignItems: "center",
          borderTopLeftRadius: "0.7rem",
          borderTopRightRadius: "0.7rem",
          color: "text.secondary",
          background: isDarkMode ? grey[900] : grey[200]
        }}
      >
        <Typography variant="caption">{match?.[1] || "Raw code"}</Typography>
        <ClipboardCopy edge="end" value={code} />
      </Stack>

      {highlightedCode}
      {nonHighlightedCode}
    </Box>
  );
};

export { Code };
