import { LibraryListItem, PlayerDevice } from "../upnpapi/types";
import IconPlayer from "../assets/icon-player.svg";

interface BrowseListItemProps {
  item: LibraryListItem;
  clickHandler?: CallableFunction;
}

export function BrowseListItem({ item, clickHandler }: BrowseListItemProps) {
  let className =
    "block flex items-center px-4 h-16 hover:bg-primary-lightest cursor-pointer text-left";
  return (
    <li
      onClick={() => {
        if (clickHandler) {
          clickHandler(item);
        }
      }}
      className={className}
    >
      {/* <img
        src={IconPlayer}
        alt=""
        className="h-14 w-14 m-1 rounded-xl border border-primary-light"
      /> */}
      {item.title}
    </li>
  );
}
