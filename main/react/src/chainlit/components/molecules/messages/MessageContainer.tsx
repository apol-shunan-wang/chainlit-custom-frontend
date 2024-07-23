import {
  MessageContext,
  defaultMessageContext
} from "chainlit/contexts/MessageContext";
import { memo } from "react";

import { IAction, IMessageElement, IStep } from "@chainlit/react-client";
import { IMessageContext } from "types/messageContext";

import { Messages } from "./Messages";

interface Props {
  actions: IAction[];
  context: IMessageContext;
  elements: IMessageElement[];
  messages: IStep[];
}

const MessageContainer = memo(
  ({ actions, context, elements, messages }: Props) => {
    return (
      <MessageContext.Provider value={context || defaultMessageContext}>
        <Messages
          indent={0}
          messages={messages}
          elements={elements}
          actions={actions}
        />
      </MessageContext.Provider>
    );
  }
);

export { MessageContainer };
