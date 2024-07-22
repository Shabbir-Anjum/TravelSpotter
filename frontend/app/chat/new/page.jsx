'use client';

import ChatLayout from "@/components/ChatLayout";
import React, { useState, useEffect } from "react";
import { AiOutlineUserAdd } from 'react-icons/ai';
import { useSelector } from "react-redux";
import { useRouter } from "next/navigation";
import {FaArrowLeft } from "react-icons/fa";

const Page = () => {
  const [name, setName] = useState('');
  const [friendInput, setFriendInput] = useState('');
  const [friends, setFriends] = useState({});
  const userdata = useSelector((state) => state.chat.userdata);
  const serverUrl = useSelector((state) => state.chat.server_url);
  const email = userdata.email;
  const router = useRouter();


  useEffect(() => {
   
  }, [friends]);

  const handleAddFriend = () => {
    if (friendInput.trim() !== '') {
      const newFriendId = Object.keys(friends).length + 1;
      setFriends({
        ...friends,
        [newFriendId]: friendInput.trim()
      });
      setFriendInput('');
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await addOuting();
      setName('');
      setFriends({});
    } catch (error) {
      console.error('Error creating outing:', error);
    }
router.push('/chat')
  };

  const addOuting = async () => {
    try {
      const response = await fetch(`${serverUrl}/api/add-outing`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          name: name, 
          email: email, 
          friend_emails: friends 
        }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to add outing');
      }
  
      return await response.json();
    } catch (error) {
      console.error('Error adding outing:', error);
      throw error;
    }
  };

  return (
    <ChatLayout>
         <button
                className=" text-black hover:text-blue-700 bg-slate-200 "
                onClick={()=>{router.push('/chat');}}
              >
                <FaArrowLeft size={20} className="ml-8 mt-3" />
              </button>
    <div className="flex items-center justify-center bg-slate-200 h-screen p-10">
      <div className="bg-white p-10 rounded-lg shadow-md w-full max-w-lg">
        <h1 className="text-2xl font-bold mb-6">Create a new Outing Group</h1>

        <input
          className="w-full p-3 border border-gray-300 rounded-md mb-4"
          type="text"
          placeholder="Enter the name of the outing"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <div className="relative flex mb-4">
          <input
            className="w-full p-3 border border-gray-300 rounded-md mr-2"
            type="text"
            placeholder="Enter Email of your friends"
            value={friendInput}
            onChange={(e) => setFriendInput(e.target.value)}
          />
          <button
            className="bg-black text-white p-3 rounded-md hover:bg-green-600"
            onClick={handleAddFriend}
          >
            <AiOutlineUserAdd size={24} />
          </button>
        </div>

        {Object.keys(friends).length > 0 && (
          <div className="mt-4">
            <h2 className="text-lg font-semibold mb-2">Selected Friends:</h2>
            <ul className="list-disc list-inside">
              {Object.entries(friends).map(([key, email]) => (
                <li key={key}>{email}</li>
              ))}
            </ul>
          </div>
        )}

        <button
          className="w-full bg-black text-white p-3 rounded-md hover:bg-green-600 mt-6"
          onClick={handleSubmit}
        >
          Create
        </button>
      </div>
    </div>
  </ChatLayout>
  );
};

export default Page;
