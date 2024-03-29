import PrevIcon from "../assets/control-prev.svg";
import NextIcon from "../assets/control-next.svg";
import PlayIcon from "../assets/control-play.svg";
import PauseIcon from "../assets/control-pause.svg";
import NavDownIcon from "../assets/nav-down.svg";
import DevicesIcon from "../assets/control-devices.svg";
import ImgPlaceholder from "../assets/track.svg";
import { TopBar } from "../components/TopBar";
import { Link, useNavigate } from "react-router-dom";
import { usePlayerControl } from "../custom-hooks";
import { PlaybackControl } from "../upnpapi";

interface PlayerProps {
  playbackControl: PlaybackControl;
}

const Player = (props: PlayerProps) => {
  const { playerPresent, playerName, volumePercent, artist, title, transport } =
    usePlayerControl(props.playbackControl);
  const navigate = useNavigate();
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
    <button>
      <img className="w-6 h-6" src={NavDownIcon} onClick={() => navigate(-1)} />
    </button>
  );
  const PlayPauseIcon =
    transport === "PLAYING" ? (
      <img alt="playing" src={PauseIcon} className="w-24 h-24 text-primary" />
    ) : (
      <img
        alt="playback stopped"
        src={PlayIcon}
        className="w-24 h-24 text-primary"
      />
    );
  const action = (
    <Link to="/select-player">
      <img className="w-6 h-6" src={DevicesIcon} />
    </Link>
  );
  return (
    <>
      <TopBar nav={nav} action={action} title={playerName} />
      <div className="container mx-auto flex flex-col w-full h-full">
        <div className="flex-grow-2">
          <img
            src={ImgPlaceholder}
            className="rounded-3xl mx-auto h-48 w-auto text-primary shadow-2xl border-primary-light border"
          />
        </div>
        <div className="flex-grow p-8 max-h-44 text-center text-primary">
          <h3 className="text-4xl font-bold">{title}</h3>
          <h4>{artist}</h4>
        </div>
        <div className="mb-4 flex justify-around items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-primary-lightest"
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
          <img src={PrevIcon} className="h-12 w-12 text-primary-lightest" />
          <button
            aria-label="PlayPause"
            onClick={() => props.playbackControl.playPause()}
          >
            {PlayPauseIcon}
          </button>
          <img src={NextIcon} className="h-12 w-12 text-primary-lightest" />
        </div>
        <div className="mb-8 p-8 flex justify-around items-center">
          <input
            type="range"
            max="100"
            min="0"
            value={volumePercent}
            onChange={changeVolume}
            name="volume"
            aria-label="Volume"
            className="max-w-md"
          />
        </div>
        <div className={overlayClass}></div>
      </div>
    </>
  );
};

export default Player;
