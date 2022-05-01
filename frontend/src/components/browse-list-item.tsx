import { LibraryListItem } from "../upnpapi/types";
import IconContainer from "../assets/folder.svg";
import IconTrack from "../assets/track.svg";
import PlayIcon from "../assets/control-play.svg";
import { LazyLoadImage } from "react-lazy-load-image-component";

interface BrowseListItemProps {
  item: LibraryListItem;
  clickHandler?: CallableFunction;
}

export function BrowseListItem({ item, clickHandler }: BrowseListItemProps) {
  let className =
    "block group flex items-center px-4 h-16 hover:bg-primary-lightest cursor-pointer text-left";
  const placeholderIcon = item.upnpclass === "item" ? IconTrack : IconContainer;
  const img = item.image ? item.image : placeholderIcon;
  const overlay =
    item.upnpclass === "item" ? (
      <div className="flex justify-center items-center absolute opacity-0 group-hover:opacity-70 m-1 rounded-xl h-14 w-14 bg-gray-800 text-white font-semibold">
        <img src={PlayIcon} className="h-10 w-10" />
      </div>
    ) : null;
  return (
    <li
      onClick={() => {
        if (clickHandler) {
          clickHandler(item);
        }
      }}
      className={className}
    >
      <LazyLoadImage
        src={img}
        alt="album art"
        className="h-14 w-14 m-1 rounded-xl object-scale-down"
        placeholderSrc={placeholderIcon}
      />
      {overlay}
      {item.title}
    </li>
  );
}
