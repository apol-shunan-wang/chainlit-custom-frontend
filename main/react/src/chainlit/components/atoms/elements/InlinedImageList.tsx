import { IImageElement } from "@chainlit/react-client";

import { ImageElement } from "./Image";
import { ListWithSize } from "./ListWithSize";

interface Props {
  items: IImageElement[];
}

const InlinedImageList = ({ items }: Props) => (
  <ListWithSize<IImageElement>
    elements={items}
    renderElement={ctx => <ImageElement element={ctx.element} />}
  />
);

export { InlinedImageList };
