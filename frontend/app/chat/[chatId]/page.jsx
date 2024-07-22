'use client';

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSelector, useDispatch } from "react-redux";
import {
  connectSocket,
  disconnectSocket,
  sendMessage,
  joinRoom,
} from "@/services/socketService";
import { setCurrentMessages, setCurrentRoom } from "@/store/ChatSlice";
import { IoSend } from "react-icons/io5";
import ChatWindow from "@/components/ChatWindow";
import ProtectedRoute from "@/components/ProtectedRoute";
import ChatLayout from "@/components/ChatLayout";
import { FaRobot,  FaArrowLeft } from "react-icons/fa";

import SubmitAIMessage from "@/components/SubmitAIMessage";
import style from "./chat.module.css";

const ChatRoom = () => {
  const [messageInput, setMessageInput] = useState("");
  const [showSubmitAIMessage, setShowSubmitAIMessage] = useState(false);
  const router = useRouter();
  const messages = useSelector((state) => state.chat.messages);
  const currentRoom = useSelector((state) => state.chat.currentRoom);
  const RoomName = useSelector((state) => state.chat.RoomName);
  const dispatch = useDispatch();
  const currentuser = useSelector((state) => state.chat.user);
  const serverUrl = useSelector((state) => state.chat.server_url);

  useEffect(() => {
    connectSocket();
    if (currentRoom) {
      handleJoin(currentRoom);
    }

    const storedMessages = JSON.parse(localStorage.getItem("chatMessages"));
    if (storedMessages) {
      dispatch(setCurrentMessages(storedMessages));
    }

    return () => {
      disconnectSocket();
    };
  }, [currentRoom]);

  const handleJoin = (currentRoom) => {
    joinRoom(currentRoom);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const datetime = new Date().toGMTString();
    sendMessage(messageInput, currentRoom, currentuser, datetime);

    fetch(`${serverUrl}/api/get-outings/${currentRoom}/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'insomnia/9.2.0'
      },
      body: JSON.stringify({
        content: messageInput,
        send_from: currentuser,
      }),
    });
    setMessageInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSubmit(e);
    }
  };

  const handleInputChange = (e) => {
    setMessageInput(e.target.value);
  };

  return (
    <ProtectedRoute>
      <ChatLayout>
        {currentRoom && (
          <>
            <header className="bg-gray-200 text-white p-4 flex justify-between ">
              <div className=" flex gap-4">  <button
                className=" text-black hover:text-blue-700"
                onClick={()=>{router.push('/');}}
              >
                <FaArrowLeft size={20} className="mr-2" />
              </button>
                <div className="text-lg pl-10 text-black">{RoomName}</div>

              </div>

              <div
                className="pr-10 text-2xl cursor-pointer text-black"
                onClick={() => {
                  setShowSubmitAIMessage(!showSubmitAIMessage);
                }}
              >
                <FaRobot />
              </div>


            </header>
            <main className="flex-1 overflow-y-auto flex flex-col-reverse bg-white p-4">
              {showSubmitAIMessage ? (
                <>
                  <div
                    className={`${style.backdrop} h-full w-full`}
                    onClick={() => {
                      setShowSubmitAIMessage(false);
                    }}
                  ></div>
                  <SubmitAIMessage
                    currentRoom={currentRoom}
                    currentuser={currentuser}
                    serverUrl={serverUrl}
                    setShowSubmitAIMessage={setShowSubmitAIMessage}
                  />
                </>
              ) : (
                ""
              )}

              <ChatWindow messages={messages} />
            </main>
            <footer className="p-4 flex items-center">
              <input
                className="flex-1 p-2 border border-gray-400 rounded focus:outline-none"
                style={{
                  background: "none",
                  resize: "none",
                  minHeight: "40px",
                }}
                placeholder="Type your message..."
                value={messageInput}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
              />
              <button
                className="ml-2 px-4 py-2 bg-black text-white rounded-lg"
                onClick={handleSubmit}
              >
                <IoSend />
              </button>
            </footer>
          </>
        )}
      </ChatLayout>
    </ProtectedRoute>
  );
};

export default ChatRoom;
