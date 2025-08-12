import { FC, useEffect, useState } from "react";
import ChatInput from "./ChatInput";
import ChatWindow from "./ChatWindow";
import Login from "./Login";
import { useUser, useUsers } from "./api/chat/v1/user_rbt_react";
import { Button } from "./components/ui/button";

const UsersPane: FC = () => {
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
        </div>
      ))}
    </>
  );
};

const LoggedInChatApp: FC<{ username: string; handleLogout: () => void }> = ({
  username,
  handleLogout,
}) => {
  const [window, setWindow] = useState<"chats">(
    "chats"
  );

  const { create } = useUser({ id: username });

  useEffect(() => {
    create();
  }, []);

  const onMessage = (message: string) => {};

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
    <LoggedInChatApp username={username} handleLogout={handleLogout} />
  );
}

export default App;
