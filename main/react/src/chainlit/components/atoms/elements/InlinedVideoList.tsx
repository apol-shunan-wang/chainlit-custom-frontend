import { IVideoElement } from "@chainlit/react-client";

import { ListWithSize } from "./ListWithSize";
import { VideoElement } from "./Video";

interface Props {
  items: IVideoElement[];
}

const InlinedVideoList = ({ items }: Props) => (
  <ListWithSize<IVideoElement>
    elements={items}
    renderElement={ctx => <VideoElement element={ctx.element} />}
  />
);

export { InlinedVideoList };
