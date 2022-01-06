import { ReactComponent as PrevIcon } from "../assets/control-prev.svg";
import { ReactComponent as NextIcon } from "../assets/control-next.svg";
import { ReactComponent as PlayIcon } from "../assets/control-play.svg";
import { ReactComponent as PauseIcon } from "../assets/control-pause.svg";
import { ReactComponent as NavDownIcon } from "../assets/nav-down.svg";
import { ReactComponent as DevicesIcon } from "../assets/control-devices.svg";
import { TopBar } from "../components/TopBar";
import { Link } from "react-router-dom";
import { usePlayerControl } from "../custom-hooks";
import { PlaybackControl } from "../upnpapi";

interface PlayerProps {
  playbackControl: PlaybackControl;
}

const Player = (props: PlayerProps) => {
  const { playerPresent, playerName, volumePercent, artist, title, transport } =
    usePlayerControl(props.playbackControl);
  let overlayClass =
    "absolute top-0 mt-16 right-0 bottom-0 left-0 opacity-90 bg-gray-50";
  if (playerPresent) {
    overlayClass += " hidden";
  }

  const changeVolume = (e: any) => {
    const targetVolume = parseInt(e.target.value);
    if (targetVolume !== volumePercent) {
      console.log(targetVolume);
      props.playbackControl.setVolume(targetVolume);
    }
  };

  const nav = (
    <Link to="/">
      <NavDownIcon />
    </Link>
  );
  const PlayPauseIcon =
    transport === "PLAYING" ? (
      <PauseIcon className="w-24 h-24 text-primary" />
    ) : (
      <PlayIcon className="w-24 h-24 text-primary" />
    );
  const action = (
    <Link to="/select-player">
      <DevicesIcon />
    </Link>
  );
  return (
    <>
      <TopBar nav={nav} action={action} title={playerName} />
      <div className="container mx-auto flex flex-col w-full h-full">
        <div className="flex-grow-2">
          <img
            className="
          rounded-3xl
          mx-auto
          h-48
          w-auto
          text-primary-light
          shadow-2xl
          border-primary-light border
        "
            src="android-chrome-192x192.png"
            alt="cover art"
          />
        </div>
        <div className="flex-grow p-8 max-h-44 text-center text-primary">
          <h3 className="text-4xl font-bold">{title}</h3>
          <h4>{artist}</h4>
        </div>
        <div className="mb-4 flex justify-around items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-primary-light"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <Link to="/player-queue">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-primary"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16m-7 6h7"
            />
          </svg>
          </Link>
        </div>
        <div className="mb-8 flex justify-around items-center">
          <PrevIcon className="h-12 w-12 text-primary" />
          {PlayPauseIcon}
          <NextIcon className="h-12 w-12 text-primary" />
        </div>
        <div className="mb-8 flex justify-around items-center">
          <input
            type="range"
            max="100"
            min="0"
            value={volumePercent}
            onChange={changeVolume}
            name="volume"
          />
        </div>
        <div className={overlayClass}></div>
      </div>
    </>
  );
};

export default Player;
