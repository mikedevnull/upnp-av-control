import { ReactComponent as NavUp } from "../assets/nav-up.svg";
import { ReactComponent as NextIcon } from "../assets/control-next.svg";
import { ReactComponent as PlayIcon } from "../assets/control-play-outline.svg";
import { Link } from "react-router-dom";

export default function Miniplayer() {
  return (
    <div className="p-4 h-16 flex items-center border-t">
      <Link to="/player">
        <NavUp />
      </Link>

      <img className="mx-2 border h-12" src="logo192.png"></img>
      <span className="m-2 text-left flex-grow">Miniplayer</span>
      <span>0:00</span>
      <div className="m-4 flex flex-row">
        <PlayIcon className="h-10 w-10 text-primary" />
        <NextIcon className="h-10 w-10 text-primary" />
      </div>
    </div>
  );
}
