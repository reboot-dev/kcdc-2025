import {
  HoverCard,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Separator } from "@/components/ui/separator";
import { FC } from "react";

const ChatMessage: FC<{
  timestamp: string;
  id: string;
  username: string;
  message: string;
  name: string;
  reactions: any;
}> = ({
  timestamp,
  id,
  message,
  name,
  reactions,
  username,
}) => {
  return (
    <HoverCard openDelay={10} closeDelay={10}>
      <div className="relative flex flex-col mb-4">
        {/* TODO: insert date in the separator. */}
        <Separator />
        <HoverCardTrigger>
          <div className="text-sm w-fit ml-4">
            {name} {new Date(Number(timestamp)).toLocaleString()}
          </div>
          <div className="inset-0 w-fit rounded-r-[6px] rounded-bl-[6px] p-2 text-sm mx-4 text-left">
            {message}
          </div>
        </HoverCardTrigger>
      </div>
    </HoverCard>
  );
};

export default ChatMessage;
