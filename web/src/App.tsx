import { FC, useEffect, useState } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import ChatWindow from "./ChatWindow";
import Login from "./Login";
import MessagesWindow from "./MessagesWindow";
import ReactionsWindow from "./ReactionWindow";
import ChatbotsWindow from "./ChatbotsWindow";
import { useChannel } from "./api/chat/v1/channel_rbt_react";
import { useUser, useUsers } from "./api/chat/v1/user_rbt_react";
import { Button } from "./components/ui/button";
// import {
//   Presence,
//   usePresenceContext,
// } from "@reboot-dev/reboot-std-react/presence";

const UsersPane: FC<{ users: string[] }> = ({ users }) => {
  // const { subscriberIds } = usePresenceContext();
  return (
    <>
      {users.map((user) => (
        <div className="flex items-center" key={user}>
          <div key={user} className="p-2">
            {decodeURIComponent(user)}
          </div>
          <span
            className={`flex w-3 h-3 me-3 ${
              //subscriberIds.includes(user)
              true ? "bg-green-500" : "bg-gray-500"
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
  const [window, setWindow] = useState<"chats" | "reactions" | "chatbots">(
    "chats"
  );
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const {
    useMessages,
    mutators: { post },
  } = useChannel({ id: "channel" });
  const { useList } = useUsers({ id: "(singleton)" });
  const { response: usersResponse } = useList();

  console.log("usersList", usersResponse);

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

  if (!usersResponse) {
    return <div>Loading...</div>;
  }

  return (
    // <Presence id={"presence"} subscriberId={username}>
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
            "m-2 bg-white text-darkgrey border hover:bg-black hover:text-white " +
            (window === "chatbots" && "bg-black text-white")
          }
          onClick={() => setWindow("chatbots")}
        >
          Chatbots
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
            <div className="border w-1/2 p-4">
              <h1 className="text-xl">Users</h1>
              <UsersPane users={usersResponse.users} />
            </div>
          </div>
        )}
        {window === "reactions" && <ReactionsWindow />}
        {window === "chatbots" && <ChatbotsWindow />}
      </div>
    </div>
    //</Presence>
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
