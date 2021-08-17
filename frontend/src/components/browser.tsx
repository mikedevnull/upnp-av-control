import { useEffect } from "react";
import { useState } from "react";
import * as library from "../upnpapi/library";
import { LibraryListItem } from "../upnpapi/types";
import { BrowseListItem as ListItemComponent } from "./browse-list-item";

interface BrowserProps {
  id?: string;
  clickHandler?: CallableFunction;
}

export default function Browser({ id, clickHandler }: BrowserProps) {
  const [items, setItems] = useState<LibraryListItem[]>([]);

  useEffect(() => {
    setItems([]);
    library.browse(id).then(setItems);
  }, [id]);
  const defaultActionHandler = (item: LibraryListItem) => {
    if (clickHandler) {
      clickHandler(item);
    }
  };
  const content = items.map((e) => (
    <ListItemComponent
      item={e}
      key={e.id}
      clickHandler={defaultActionHandler}
    />
  ));
  return (
    <div className="flex-grow pb-16">
      <ul>{content}</ul>
    </div>
  );
}
