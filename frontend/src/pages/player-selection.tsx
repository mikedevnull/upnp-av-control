import { TopBar, PlayerListItem } from "../components";
import { ReactComponent as NavBackIcon } from "../assets/nav-back.svg";
import { Link } from "react-router-dom";
import { PlayerDevice } from "../upnpapi/types";
import { useState } from "react";

const fake_devices: Array<PlayerDevice> = [
  {
    id: "12345",
    name: "Radio1",
  },
  {
    id: "abcdf",
    name: "TV",
  },
  {
    id: "54321",
    name: "Radio2",
  },
];

interface PlayerSelectionProps {
  devices: [PlayerDevice];
  selectedPlayerId?: string;
}

export default function PlayerSelection() {
  const nav = (
    <Link to="/player">
      <NavBackIcon />
    </Link>
  );
  let [selectedId, setSelectedId] = useState(undefined);
  const devices = fake_devices;
  const entries = devices.map((player) => (
    <PlayerListItem
      key={player.id}
      clickHandler={setSelectedId}
      player={player}
      selected={player.id === selectedId}
    />
  ));

  return (
    <>
      <TopBar nav={nav} /> <div>{entries}</div>
    </>
  );
}
