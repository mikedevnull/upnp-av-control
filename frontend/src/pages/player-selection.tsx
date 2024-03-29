import { TopBar, PlayerListItem } from "../components";
import NavBackIcon from "../assets/nav-back.svg";
import { useNavigate } from "react-router-dom";
import { PlayerDevice } from "../upnpapi/types";

interface PlayerSelectionProps {
  devices: PlayerDevice[];
  selectedPlayerId?: string;
  selectionHandler?: CallableFunction;
}

export default function PlayerSelection(props: PlayerSelectionProps) {
  const navigate = useNavigate();
  const nav = (
    <button>
      <img className="w-6 h-6" src={NavBackIcon} onClick={() => navigate(-1)} />
    </button>
  );

  const entries = props.devices.map((player) => (
    <PlayerListItem
      clickHandler={props.selectionHandler}
      key={player.id}
      player={player}
      selected={player.id === props.selectedPlayerId}
    />
  ));

  return (
    <>
      <TopBar nav={nav} /> <div>{entries}</div>
    </>
  );
}
