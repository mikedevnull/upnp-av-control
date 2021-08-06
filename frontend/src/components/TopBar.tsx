import { ReactComponent as NavBackIcon } from "../assets/nav-back.svg";
import PropTypes from "prop-types";

interface TopBarProps {
  nav?: PropTypes.ReactNodeLike;
  title?: string;
  action?: PropTypes.ReactNodeLike;
}

export const TopBar = ({ nav, title, action }: TopBarProps) => {
  nav = nav || <span className="w-6" />;
  const extraAction = action || <span className="w-6" />;
  return (
    <div className="p-4 mb-2 h-16 flex justify-between items-center border-b">
      {nav}
      <span>{title}</span>
      {extraAction}
    </div>
  );
};
