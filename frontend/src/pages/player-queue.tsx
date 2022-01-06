import { ReactComponent as NavBackIcon } from "../assets/nav-back.svg";
import IconTrack from "../assets/track.svg";
import { TopBar } from "../components/TopBar";
import { useHistory } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../upnpapi";
import { PlaybackQueueItem } from "../upnpapi/types";

interface PlayerQueueProps {
  selectedPlayerId?: string;
}

const PlayerQueue = (props: PlayerQueueProps) => {
  const history = useHistory();
  const nav = (
    <button>
      <NavBackIcon onClick={() => history.goBack()} />
    </button>
  );
  const [queueItems, setQueueItems] = useState<PlaybackQueueItem[]>([]);
  const [activeQueueIndex, setActiveQueueIndex] = useState<number | null>();
  const placeholderIcon = IconTrack;

  useEffect(() => {
    if (props.selectedPlayerId) {
      api.getPlaybackQueue(props.selectedPlayerId).then((queue) => {
        setQueueItems(queue.items);
        setActiveQueueIndex(queue.currentItemIndex);
      });
    }
  }, [props.selectedPlayerId]);
  const normalClass = "block group flex items-center px-4 h-16 text-left";
  const selectedClass = normalClass + " bg-primary-lightest";
  const content = queueItems.map((i, idx) => (
    <li
      key={i.id}
      className={idx === activeQueueIndex ? selectedClass : normalClass}
    >
      <img
        src={i.image ? i.image : placeholderIcon}
        alt="album art"
        className="h-14 w-14 m-1 rounded-xl object-scale-down"
      />
      <div className="flex flex-col items-start justify-center">
        <span>{i.title}</span>{" "}
        <span className="text-sm">
          {i.artist} - {i.album}
        </span>
      </div>
    </li>
  ));

  return (
    <>
      <TopBar nav={nav} title="Playback queue" />
      <div className="container mx-auto flex flex-col w-full h-full"></div>
      <div className="flex-grow pb-16">
        <ul>{content}</ul>
      </div>
    </>
  );
};

export default PlayerQueue;
