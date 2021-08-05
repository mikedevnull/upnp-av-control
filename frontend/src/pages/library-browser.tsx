import { TopBar, Miniplayer, Browser } from "../components";

export default function LibraryBrowser() {
  return (
    <div className="App">
      <div className="h-screen w-full flex flex-col">
        <TopBar />
        <Browser></Browser>
        <Miniplayer></Miniplayer>
      </div>
    </div>
  );
}
