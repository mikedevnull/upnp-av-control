import { PlaybackControl } from "../upnpapi";
import { useBackendConnectionState } from "../custom-hooks";
interface BackendStateViewProps {
  playbackControl: PlaybackControl;
}

export default function BackendConnectionStateView({
  playbackControl,
}: BackendStateViewProps) {
  const connectionState = useBackendConnectionState(playbackControl);
  const classNames =
    connectionState === "connected"
      ? "hidden"
      : "border border-red-700 bg-red-100 p-2";
  return (
    <div className={classNames}>ERROR: No connection to backend service.</div>
  );
}
