import {
  Presence,
  usePresenceContext,
} from "@reboot-dev/reboot-std-react/presence";
import { FC, useEffect, useState } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import ChatWindow from "./ChatWindow";
import Login from "./Login";
import MessagesWindow from "./MessagesWindow";
import { useChannel } from "./api/chat/v1/channel_rbt_react";
import { useUser, useUsers } from "./api/chat/v1/user_rbt_react";
import { Button } from "./components/ui/button";

const UsersPane: FC = () => {
  const { subscriberIds } = usePresenceContext();

  const { useList } = useUsers({ id: "(singleton)" });

  const { response } = useList();

  if (!response) {
    return <div>Loading...</div>;
  }

  const users = response.users;

  return (
    <>
      {users.map((user) => (
        <div className="flex items-center" key={user}>
          <div key={user} className="p-2">
            {decodeURIComponent(user)}
          </div>
          <span
            className={`flex w-3 h-3 me-3 ${
              subscriberIds.includes(user) ? "bg-green-500" : "bg-gray-500"
            } rounded-full`}
          ></span>
        </div>
      ))}
    </>
  );
};


const PAGE_SIZE = 20;
const LoggedInChatApp: FC<{ username: string; handleLogout: () => void }> = ({
  username,
  handleLogout,
}) => {
  const [window, setWindow] = useState<"chats">(
    "chats"
  );
  const [limit, setLimit] = useState(20);

  const { post, useMessages } = useChannel({ id: "channel" });

  const onMessage = (message: string) => {
    post({ author: username, text: message });
  };

  const { response } = useMessages({ limit });

  const messages = (response && response.messages) || {};

  const { create } = useUser({ id: username });

  useEffect(() => {
    create();
  }, []);

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
            "m-2 bg-white text-darkgrey border hover:bg-black hover:text-white "
          }
          onClick={handleLogout}
        >
          Logout
        </Button>
      </div>
      <div className="w-3/4">
        {window === "chats" && (
          <div className="flex h-screen">
            <ChatWindow>
              <MessagesWindow
                onReachTop={() => setLimit((limit) => limit + PAGE_SIZE)}
              >
                {Object.keys(messages)
                  .sort()
                  .reverse()
                  .map((timestamp) => (
                    <ChatMessage
                      timestamp={timestamp}
                      id={messages[timestamp].id}
                      username={username}
                      message={messages[timestamp].text}
                      name={messages[timestamp].author}
                      key={messages[timestamp].id}
                      reactions={messages[timestamp].reactions}
                    />
                  ))}
              </MessagesWindow>
              <ChatInput onSubmit={onMessage} />
            </ChatWindow>
            <div className="border w-1/2 p-4">
              <h1 className="text-xl">Users</h1>
              <UsersPane />
            </div>
          </div>
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

  return (
    <Presence id={"presence"} subscriberId={username}>
      <LoggedInChatApp username={username} handleLogout={handleLogout} />
    </Presence>
  );
}

export default App;
