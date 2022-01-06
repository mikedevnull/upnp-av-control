import { LibraryListItem } from "../upnpapi/types";
import { BrowseListItem as ListItemComponent } from "./browse-list-item";

interface BrowserProps {
  items: LibraryListItem[];
  clickHandler?: CallableFunction;
}

export default function Browser({ items, clickHandler }: BrowserProps) {
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
