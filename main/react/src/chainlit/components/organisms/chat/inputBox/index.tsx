import { memo, useCallback } from "react";
import { useSetRecoilState } from "recoil";
import { v4 as uuidv4 } from "uuid";

import { Box } from "@mui/material";

import { useAuth } from "@chainlit/react-client";
import { FileSpec, IStep, useChatInteract } from "@chainlit/react-client";

import ScrollDownButton from "chainlit/components/atoms/buttons/scrollDownButton";

import { useLayoutMaxWidth } from "chainlit/hooks/useLayoutMaxWidth";

import { IAttachment } from "chainlit/state/chat";
import { inputHistoryState } from "chainlit/state/userInputHistory";

import Input from "./input";
import WaterMark from "./waterMark";

interface Props {
  fileSpec: FileSpec;
  onFileUpload: (payload: File[]) => void;
  onFileUploadError: (error: string) => void;
  setAutoScroll: (autoScroll: boolean) => void;
  autoScroll?: boolean;
}

const InputBox = memo(
  ({
    fileSpec,
    onFileUpload,
    onFileUploadError,
    setAutoScroll,
    autoScroll,
  }: Props) => {
    const layoutMaxWidth = useLayoutMaxWidth();
    const setInputHistory = useSetRecoilState(inputHistoryState);

    const { user } = useAuth();
    const { sendMessage, replyMessage } = useChatInteract();
    // const tokenCount = useRecoilValue(tokenCountState);

    const onSubmit = useCallback(
      async (msg: string, attachments?: IAttachment[]) => {
        const message: IStep = {
          threadId: "",
          id: uuidv4(),
          name: user?.identifier || "User",
          type: "user_message",
          output: msg,
          createdAt: new Date().toISOString(),
        };

        setInputHistory((old) => {
          const MAX_SIZE = 50;
          const inputs = [...(old.inputs || [])];
          inputs.push({
            content: msg,
            createdAt: new Date().getTime(),
          });

          return {
            ...old,
            inputs:
              inputs.length > MAX_SIZE
                ? inputs.slice(inputs.length - MAX_SIZE)
                : inputs,
          };
        });

        const fileReferences = attachments
          ?.filter((a) => !!a.serverId)
          .map((a) => ({ id: a.serverId! }));

        setAutoScroll(true);
        sendMessage(message, fileReferences);
      },
      [user, sendMessage]
    );

    const onReply = useCallback(
      async (msg: string) => {
        const message: IStep = {
          threadId: "",
          id: uuidv4(),
          name: user?.identifier || "User",
          type: "user_message",
          output: msg,
          createdAt: new Date().toISOString(),
        };

        replyMessage(message);
        setAutoScroll(true);
      },
      [user, replyMessage]
    );

    return (
      <Box
        display="flex"
        position="relative"
        flexDirection="column"
        gap={1}
        pb={2}
        px={2}
        sx={{
          boxSizing: "border-box",
          width: "100%",
          maxWidth: layoutMaxWidth,
          m: "auto",
          justifyContent: "center",
        }}
      >
        {!autoScroll ? (
          <ScrollDownButton onClick={() => setAutoScroll(true)} />
        ) : null}
        <Box>
          <Input
            fileSpec={fileSpec}
            onFileUpload={onFileUpload}
            onFileUploadError={onFileUploadError}
            onSubmit={onSubmit}
            onReply={onReply}
          />
          {/* {tokenCount > 0 && ( */}
          {/* <Stack flexDirection="row" alignItems="center">
          <Typography
            sx={{ ml: 'auto' }}
            color="text.secondary"
            variant="caption"
          >
            Token usage: {tokenCount}
          </Typography>
        </Stack> */}
          {/* )} */}
        </Box>
        {/* <WaterMark /> */}
      </Box>
    );
  }
);

export default InputBox;
