import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import { IoMdMenu, IoMdClose } from 'react-icons/io';

const ChatLayout = ({ children }) => {
  const [hamburg, setHamburg] = useState(false); // Initially hide sidebar

  const toggleHamburg = () => {
    setHamburg(!hamburg);
  };

  return (
    <section className="h-screen flex relative">
      {/* Hamburger Menu (only visible on small screens) */}
      <div className={`absolute top-4 left-12 text-3xl cursor-pointer md:hidden z-10 ${hamburg ? 'hidden' : 'block'}`} onClick={toggleHamburg}>
        <IoMdMenu />
      </div>
      
      {/* Sidebar */}
      <Sidebar hamburg={hamburg} setHamburg={setHamburg} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {children}
      </div>
    </section>
  );
};

export default ChatLayout;
