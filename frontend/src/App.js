import { useEffect, useState } from "react";
import "./App.css";
import Player from "./player";
import UpnpApi from "./upnpapi";
import { PlaybackControl, ControlPointEventBus } from "./upnpapi";

const api = new UpnpApi();
const bus = new ControlPointEventBus();
const playbackControl = new PlaybackControl(bus);
function App() {
  const [renderers, setRenderers] = useState([]);

  return (
    <div className="App">
      <Player devices={playbackControl.availablePlayers} />
    </div>
  );
}

export default App;
