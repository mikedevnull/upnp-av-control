import { PlayerDevice } from "../upnpapi/types";
import IconPlayer from "../assets/icon-player.svg";

interface PlayerListItemProps {
  player: PlayerDevice;
  selected?: boolean;
  clickHandler?: CallableFunction;
}

export default function PlayerListItem({
  player,
  selected = false,
  clickHandler,
}: PlayerListItemProps) {
  let className = "block flex items-center px-4 h-16 hover:bg-primary-lightest";
  if (selected) {
    className += " bg-primary-lightest";
  }
  return (
    <li
      onClick={() => {
        if (clickHandler) {
          clickHandler(player.id);
        }
      }}
      className={className}
    >
      <img
        src={IconPlayer}
        alt=""
        className="h-14 w-14 m-1 rounded-xl object-scale-down"
      />
      {player.name}
    </li>
  );
}
