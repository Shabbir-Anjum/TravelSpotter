'use client';

import React, { useState } from 'react';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '@/services/firebase/config';
import { useRouter } from 'next/navigation'; 
import { signOut } from 'firebase/auth';
import { FiMenu, FiX } from 'react-icons/fi';

import ProtectedRoute from '@/components/ProtectedRoute';

const Home = () => {
  const [user] = useAuthState(auth);
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    signOut(auth).then(() => {
      sessionStorage.removeItem('user');
      router.push('/sign-in');
    });
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <ProtectedRoute>
      <div className="bg-cover flex flex-col justify-center bg-center h-screen" style={{ backgroundImage: 'url("https://www.qexperiences.in/blog/wp-content/uploads/2021/07/duy-pham-Cecb0_8Hx-o-unsplash-scaled.jpg")' }}>
        {/* Overlay */}
        <div className="bg-black bg-opacity-50 h-full">
          {/* Navigation Bar */}
          <nav className="p-4 flex justify-between items-center text-white">
            <h1 className="text-2xl font-bold">Outing App</h1>
            <div className="md:hidden z-50">
              <button onClick={toggleMenu} className="focus:outline-none ">
                {isMenuOpen ? <FiX className="w-6 h-6" /> : <FiMenu className="w-6 h-6" />}
              </button>
            </div>
            <ul className={`fixed inset-0 flex flex-col items-center justify-center bg-black md:bg-transparent bg-opacity-75 transition-transform transform ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'} md:static md:flex md:flex-row md:items-center md:space-x-8 md:pr-10`}>
              <li> <button onClick={()=>router.push('/profile')} className="block md:inline-block py-8 md:py-0 hover:underline">Profile</button></li>
              <li> <button onClick={()=>router.push('/chat')} className="block md:inline-block py-8 md:py-0 hover:underline">Chat</button></li>
              <li><button onClick={handleLogout} className="block md:inline-block py-8 md:py-0 hover:underline">Log out</button></li>
            </ul>
          </nav>

          {/* Main Content */}
          <div className="text-center text-white mt-20">
            <h2 className="text-4xl font-bold">Discover Amazing Adventures with Friends</h2>
            <p className="mt-4">Never run out of outing ideas again!</p>
            <button onClick={()=>router.push('/chat/new')} className="mt-8 px-6 py-3 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700">Create Outing</button>
          </div>

          {/* Footer */}
          <footer className="text-center bg-black absolute bottom-0 w-full text-white p-2">
            <p>&copy; 2024 Outing App. All rights reserved.</p>
          </footer>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default Home;
