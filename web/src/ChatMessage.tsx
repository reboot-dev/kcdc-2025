import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useMessage } from "./api/chat/v1/message_rbt_react";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { BookmarkIcon, ChatBubbleIcon, FaceIcon } from "@radix-ui/react-icons";
import EmojiPicker, { EmojiClickData } from "emoji-picker-react";
import { FC } from "react";
import Reaction from "./Reaction";

const ChatMessage: FC<{
  id: string;
  username: string;
  message: string;
  name: string;
  reactions: any;
}> = ({ id, message, name, reactions, username }) => {
  const {
    mutators: { addReaction },
  } = useMessage({ id });

  const handleThumbsUp = () => {
    addReaction({ unicode: "👍", author: username });
  };

  const handleEmojiSelection = (emojiData: EmojiClickData) => {
    addReaction({ unicode: emojiData.emoji, author: username });
  };

  return (
    <HoverCard openDelay={10} closeDelay={10}>
      <div className="relative flex flex-col mb-4">
        {/* TODO: insert date in the separator. */}
        <Separator />
        <HoverCardTrigger>
          <div className="text-sm w-fit ml-4">
            {name} ({id.replace("message-", "")})
          </div>
          <div className="inset-0 w-fit rounded-r-[6px] rounded-bl-[6px] p-2 text-sm mx-4 text-left">
            {message}
          </div>
        </HoverCardTrigger>
        <div className="flex ml-4 mt-2">
          {Object.entries(reactions)
            .sort((left, right) => {
              return left[0].localeCompare(right[0]);
            })
            .map(([reaction, authors]) => (
              <Reaction
                reaction={[reaction, authors.ids.length]}
                messageId={id}
                className="mr-1 p-1"
                active={authors.ids.indexOf(username) > -1}
                authors={authors.ids}
                username={username}
              />
            ))}
        </div>
      </div>
      <HoverCardContent
        align="end"
        side="top"
        sideOffset={-48}
        alignOffset={1}
        className="shadow-none p-0 mr-2 w-44"
      >
        <div className="flex flex-col justify-end">
          <Popover>
            <TooltipProvider>
              <div className="flex justify-between">
                <Tooltip>
                  <TooltipTrigger>
                    <Button
                      variant="outline"
                      size="icon"
                      className="border-0"
                      onClick={handleThumbsUp}
                    >
                      👍
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>+1</p>
                  </TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        size="icon"
                        className="border-0"
                      >
                        <FaceIcon />
                      </Button>
                    </PopoverTrigger>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Add reaction</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger>
                    <Button
                      variant="outline"
                      size="icon"
                      className="border-0"
                      disabled
                    >
                      <ChatBubbleIcon />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Reply in thread</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger>
                    <Button
                      variant="outline"
                      size="icon"
                      className="border-0"
                      disabled
                    >
                      <BookmarkIcon />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Save for later</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </TooltipProvider>
            <PopoverContent className="w-fit border-none p-0 mr-2">
              <EmojiPicker onEmojiClick={handleEmojiSelection} />
            </PopoverContent>
          </Popover>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export default ChatMessage;
