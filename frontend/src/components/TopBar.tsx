interface TopBarProps {
  nav?: JSX.Element | JSX.Element[];
  title?: string;
  action?: JSX.Element | JSX.Element[];
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
