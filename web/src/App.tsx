import { FC, useEffect, useState } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import ChatWindow from "./ChatWindow";
import Login from "./Login";
import MessagesWindow from "./MessagesWindow";
import ReactionsWindow from "./ReactionWindow";
import { useChannel } from "./api/chat/v1/channel_rbt_react";
import { useUser } from "./api/chat/v1/user_rbt_react";
import { Button } from "./components/ui/button";

const PAGE_SIZE = 20;
const LoggedInChatApp: FC<{ username: string; handleLogout: () => void }> = ({
  username,
  handleLogout,
}) => {
  const [window, setWindow] = useState<"chats" | "reactions">("chats");
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const {
    useMessages,
    mutators: { post },
  } = useChannel({ id: "channel" });

  const onMessage = (message: string) => {
    post({ author: username, text: message });
  };

  const {
    mutators: { create },
  } = useUser({ id: username });

  useEffect(() => {
    create().then(() => console.log("user created"));
  }, []);

  const { response } = useMessages({ itemsPerPage });
  const details = (response && response.details) || [];

  return (
    <div className="flex">
      <div className="w-1/4 border-r flex flex-col p-4 h-screen">
        <Button
          className={
            "m-2 bg-white text-darkgrey border hover:bg-black hover:text-white " +
            (window === "chats" && "bg-black text-white")
          }
          onClick={() => setWindow("chats")}
        >
          Chats
        </Button>
        <Button
          className={
            "m-2 bg-white text-darkgrey border hover:bg-black hover:text-white " +
            (window === "reactions" && "bg-black text-white")
          }
          onClick={() => setWindow("reactions")}
        >
          Reactions
        </Button>
        <Button
          className={
            "m-2 bg-white text-darkgrey border hover:bg-black hover:text-white "
          }
          onClick={handleLogout}
        >
          Logout
        </Button>
      </div>
      <div className="w-3/4">
        {window === "chats" ? (
          <ChatWindow>
            <MessagesWindow
              onReachTop={() =>
                setItemsPerPage((itemsPerPage) => itemsPerPage + PAGE_SIZE)
              }
            >
              {[...details]
                .reverse()
                .map(
                  ({
                    id,
                    author,
                    text,
                    reactions,
                  }: {
                    id: string;
                    author: string;
                    text: string;
                    reactions: any;
                  }) => (
                    <ChatMessage
                      id={id}
                      username={username}
                      message={text}
                      name={author}
                      key={id}
                      reactions={reactions}
                    />
                  )
                )}
            </MessagesWindow>
            <ChatInput onSubmit={onMessage} />
          </ChatWindow>
        ) : (
          <ReactionsWindow />
        )}
      </div>
    </div>
  );
};

function App() {
  const usernameLocalStorage = localStorage.getItem("username");
  let [username, setUsername] = useState(usernameLocalStorage || undefined);

  const handleLogout = () => {
    setUsername(undefined);
    localStorage.removeItem("username");
  };

  const handleLogin = (username: string) => {
    setUsername(username);
    localStorage.setItem("username", username);
  };

  if (username === undefined) return <Login onSubmit={handleLogin} />;

  return <LoggedInChatApp username={username} handleLogout={handleLogout} />;
}

export default App;
