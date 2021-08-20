import { LibraryListItem } from "../upnpapi/types";
import IconContainer from "../assets/folder.svg";
import IconTrack from "../assets/track.svg";

interface BrowseListItemProps {
  item: LibraryListItem;
  clickHandler?: CallableFunction;
}

export function BrowseListItem({ item, clickHandler }: BrowseListItemProps) {
  let className =
    "block flex items-center px-4 h-16 hover:bg-primary-lightest cursor-pointer text-left";
  const placeholderIcon = item.upnpclass === "item" ? IconTrack : IconContainer;
  const img = item.image ? item.image : placeholderIcon;
  return (
    <li
      onClick={() => {
        if (clickHandler) {
          clickHandler(item);
        }
      }}
      className={className}
    >
      <img
        src={img}
        alt=""
        className="h-14 w-14 m-1 rounded-xl object-scale-down"
      />
      {item.title}
    </li>
  );
}
