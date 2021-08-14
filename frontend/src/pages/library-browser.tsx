import { TopBar, Miniplayer, Browser } from "../components";
import { PlaybackControl } from "../upnpapi";
interface LibraryBrowserProps {
  playbackControl: PlaybackControl;
}

export default function LibraryBrowser(props: LibraryBrowserProps) {
  return (
    <div className="App">
      <div className="h-screen w-full flex flex-col">
        <TopBar />
        <Browser></Browser>
        <Miniplayer playbackControl={props.playbackControl}></Miniplayer>
      </div>
    </div>
  );
}
