import { Separator } from "@/components/ui/separator";
import { FC, useState } from "react";
import { useUser } from "./api/chat/v1/user_rbt_react";

const PAGE_SIZE = 40;
const ReactionsWindow: FC<{}> = () => {
  const username = localStorage.getItem("username");

  const [itemsPerPage, setItemsPerPage] = useState(40);
  const { useGetMessagesReactions } = useUser({ id: username });

  const { response } = useGetMessagesReactions({ page: -1, itemsPerPage });

  const reactions = (response && response.reactions) || [];

  const handleScroll = (e: React.UIEvent<HTMLElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target as HTMLElement;
    const position = Math.ceil(
      (scrollTop / (scrollHeight - clientHeight)) * 100
    );

    if (position === 100) {
      setItemsPerPage((itemsPerPage) => itemsPerPage + PAGE_SIZE);
    }
  };

  return (
    <div onScroll={handleScroll} className="relative h-screen overflow-y-auto">
      {[...reactions].reverse().map((reaction) => {
        return (
          <>
            <div className="p-4">
              {reaction.author} reacted with {reaction.unicode} to your message{" "}
              <i>"{reaction.snippet}"</i>
            </div>
            <Separator />
          </>
        );
      })}
    </div>
  );
};

export default ReactionsWindow;
