import { ReactComponent as PrevIcon } from "../assets/control-prev.svg";
import { ReactComponent as NextIcon } from "../assets/control-next.svg";
import { ReactComponent as PlayIcon } from "../assets/control-play.svg";
import { ReactComponent as NavDownIcon } from "../assets/nav-down.svg";
import { ReactComponent as DevicesIcon } from "../assets/control-devices.svg";
import { TopBar } from "../components/TopBar";
import { Link } from "react-router-dom";

const Player = () => {
  const current_volume = 0;
  const current_title = "Dummy Title";
  const current_artist = "Dummy Artist";
  const nav = (
    <Link to="/">
      <NavDownIcon />
    </Link>
  );
  const action = (
    <Link to="/select-player">
      <DevicesIcon />
    </Link>
  );
  return (
    <>
      <TopBar nav={nav} action={action} />
      <div className="container flex flex-col w-full h-full">
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
            src="logo192.png"
            alt="cover art"
          />
        </div>
        <div className="flex-grow p-8 max-h-44 text-center text-primary">
          <h3 className="text-4xl font-bold">{current_title}</h3>
          <h4>{current_artist}</h4>
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
        </div>
        <div className="mb-8 flex justify-around items-center">
          <PrevIcon className="h-12 w-12 text-primary" />
          <PlayIcon className="w-24 h-24 text-primary" />
          <NextIcon className="h-12 w-12 text-primary" />
        </div>
        <div className="mb-8 flex justify-around items-center">
          <input
            type="range"
            max="100"
            min="0"
            value={current_volume}
            name="volume"
          />
        </div>
      </div>
    </>
  );
};

export default Player;
