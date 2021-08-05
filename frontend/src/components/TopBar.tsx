import {ReactComponent as NavBackIcon} from "../assets/nav-back.svg";

export const TopBar = () => {
  return <div className="p-4 h-16 flex justify-between items-center border-b">
      <NavBackIcon className="h-6 w-6 text-primary" />
      <span></span>
      <span className="w-6" />
    </div>
  
};
