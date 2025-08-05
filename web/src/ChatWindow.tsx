import React, { FC } from "react";
const ChatWindow: FC<{ children: React.ReactNode }> = ({ children }) => {
  return <div className="relative h-screen">{children}</div>;
};

export default ChatWindow;
