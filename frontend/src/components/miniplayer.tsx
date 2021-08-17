import { ReactComponent as NavUp } from "../assets/nav-up.svg";
import { ReactComponent as NextIcon } from "../assets/control-next.svg";
import { ReactComponent as PlayIcon } from "../assets/control-play-outline.svg";
import { Link } from "react-router-dom";
import { PlaybackControl } from "../upnpapi";
import { usePlayerControl } from "../custom-hooks";

interface MiniplayerProps {
  playbackControl: PlaybackControl;
}

export default function Miniplayer({ playbackControl }: MiniplayerProps) {
  const { playerPresent, title, artist } = usePlayerControl(playbackControl);
  let main;
  if (playerPresent) {
    main = (
      <>
        <img
          className="mx-2 border h-12"
          src="logo192.png"
          alt="cover art"
        ></img>
        <div className="flex flex-col flex-grow justify-center">
          <span className="text-left">{title}</span>
          <span className="text-left text-sm">{artist}</span>
        </div>
        <div className="m-4 flex flex-row">
          <PlayIcon className="h-10 w-10 text-primary" />
          <NextIcon className="h-10 w-10 text-primary" />
        </div>
      </>
    );
  } else {
    main = <span>No player present</span>;
  }

  return (
    <div className="p-4 h-16 flex items-center border-t w-full bg-white fixed bottom-0">
      <Link to="/player">
        <NavUp />
      </Link>
      {main}
    </div>
  );
}
