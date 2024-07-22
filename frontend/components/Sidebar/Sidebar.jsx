// Sidebar.jsx

import React, { useEffect, useState } from "react";
import { IoMdClose } from "react-icons/io";
import { FiSearch, FiPlus } from "react-icons/fi";
import { useRouter } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import {
  setCurrentRoom,
  setCurrentMessages,
  setRoomName
} from "@/store/ChatSlice";
import { getMessages, listOutings } from "@/API/Api";

const Sidebar = ({ hamburg, setHamburg }) => {
  const [searchInput, setSearchInput] = useState("");
  const router = useRouter();
  const dispatch = useDispatch();
  const serverUrl = useSelector((state) => state.chat.server_url);
  const userdata = useSelector((state) => state.chat.userdata);
  const [outings, setOutings] = useState([]);
  const [error, setError] = useState("");

  const handleRoomClick = async (currentRoom, RoomName) => {
    try {
      const response = await getMessages(serverUrl, currentRoom); // Pass serverUrl as an argument
      dispatch(setCurrentMessages(response.messages));
      localStorage.setItem("chatMessages", JSON.stringify(response.messages));
      setHamburg(false);
      dispatch(setCurrentRoom(currentRoom));
      dispatch(setRoomName(RoomName));
      router.push(`/chat/${currentRoom}`);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSearchChange = (e) => {
    setSearchInput(e.target.value);
  };

  const filteredOutings = outings.filter((outing) =>
    outing.name.toLowerCase().includes(searchInput.toLowerCase())
  );

  useEffect(() => {
    const fetchUserOutings = async () => {
      try {
        const data = await listOutings(serverUrl, userdata.email); // Use the getOutings function
        setOutings(data.outings);


        setError('');
      } catch (error) {
        console.error('Error fetching outings:', error);
        setError(error.message);
      }
    };

    if (userdata.email) {
      fetchUserOutings();
    }
  }, [userdata, serverUrl]);

  const photoURL = userdata?.photoURL || 'default-image-url.jpg';

  return (
    <div
      className={`fixed md:static top-0 left-0 h-full z-10 md:w-80 w-screen max-w-md bg-white border-r border-gray-400 transition-transform transform ${hamburg ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0`}
    >
      <div
        className="absolute top-4 right-4 text-3xl cursor-pointer md:hidden"
        onClick={() => setHamburg(false)}
      >
        <IoMdClose />
      </div>
      <div className="flex flex-col h-full">
        <div className="p-6 border-b border-gray-400">
          <h1 className="text-xl mb-4">Outings</h1>
          <div className="flex items-center border border-gray-400 rounded-lg overflow-hidden">
            <FiSearch className="w-6 h-6 mx-2 text-gray-500" />
            <input
              type="text"
              className="flex-1 p-2 focus:outline-none"
              placeholder="Search"
              value={searchInput}
              onChange={handleSearchChange}
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          <ul className="space-y-4">
            {filteredOutings.map((item, index) => (
              <li
                key={index}
                className="p-4 bg-gray-100 rounded-lg shadow cursor-pointer"
                onClick={() => handleRoomClick(item.id,item.name)} 
              >
                <div className="text-lg">{item.name}</div>
              </li>
            ))}

          </ul>
          {error && <p className="text-red-500">{error}</p>}
        </div>
        <div className="p-6 border-t border-gray-400 flex items-center justify-between bg-white">
          <div
            className="w-12 h-12 bg-gray-300 cursor-pointer rounded-full bg-cover bg-center"
            style={{ backgroundImage: `url(${photoURL})` }}
            onClick={() => {
              router.push("/profile");
            }}
          ></div>
          <button
            className="flex items-center justify-center px-4 py-2 bg-black text-white rounded-lg"
            onClick={() => {
              router.push("/chat/new");
            }}
          >
            <FiPlus className="mr-2" /> New
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
