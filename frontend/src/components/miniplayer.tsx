import { ReactComponent as NavUp } from "../assets/nav-up.svg";
import { ReactComponent as NextIcon } from "../assets/control-next.svg";
import { ReactComponent as PlayIcon } from "../assets/control-play.svg";
import { ReactComponent as PauseIcon } from "../assets/control-pause.svg";
import ImgPlaceholder from "../assets/track.svg";
import { Link } from "react-router-dom";
import { PlaybackControl } from "../upnpapi";
import { usePlayerControl } from "../custom-hooks";

interface MiniplayerProps {
  playbackControl: PlaybackControl;
}

export default function Miniplayer({ playbackControl }: MiniplayerProps) {
  const { playerPresent, title, artist, transport } =
    usePlayerControl(playbackControl);
  let main;
  const PlayPauseIcon =
    transport === "PLAYING" ? (
      <PauseIcon className="w-10 h-10 text-primary" />
    ) : (
      <PlayIcon className="w-10 h-10 text-primary" />
    );
  if (playerPresent) {
    main = (
      <>
        <img
          className="mx-2 border h-12 rounded-xl"
          src={ImgPlaceholder}
          alt="cover art"
        ></img>
        <div className="flex flex-col flex-grow justify-center">
          <span className="text-left">{title}</span>
          <span className="text-left text-sm">{artist}</span>
        </div>
        <div className="m-4 flex flex-row">
          <button onClick={() => playbackControl.playPause()}>
          {PlayPauseIcon}
          </button>
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
