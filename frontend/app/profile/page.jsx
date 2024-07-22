'use client';
import React, { useState } from 'react'; // Import useState for state management
import { MdKeyboardArrowLeft } from 'react-icons/md'; // Import React icons
import { useRouter } from 'next/navigation'; // Import useRouter for navigation
import CustomInput from '@/components/common/CustomInput'; // Import your custom input component
import { FaUserEdit } from "react-icons/fa";
import { FaSave } from "react-icons/fa";
import { useSelector} from 'react-redux';
import ProtectedRoute from '@/components/ProtectedRoute';
const Profile = () => {
  
  const router = useRouter();
  const [editMode, setEditMode] = useState(false); // State for edit mode
  const [name, setName] = useState(null); // Example name
 // const [userId, setUserId] = useState('ghostfreak123'); // Example user ID
  const [email, setEmail] = useState(null); // Example email
  const [link, setLink] = useState('https://example.com'); // Example link
  const [bio, setBio] = useState('Frontend Developer'); // Example bio
  const userdata = useSelector((state) => state.chat.userdata);
  const handleEditToggle = () => {
    setEditMode(!editMode);
  };
  const photoURL = userdata?.photoURL || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330';
  const displayName = userdata?.displayName || 'name'
  const Email = userdata?.email|| 'userid'
  return (
    <ProtectedRoute>
    <div className="min-h-screen bg-gray-200 flex items-center justify-center ">
    <div className="max-w-md w-full bg-gray-200 shadow-lg rounded-lg overflow-hidden">
      <div className="bg-cover bg-center h-40" style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1494790108377-be9c29b29330")' }}>
        <MdKeyboardArrowLeft
          className="text-white text-3xl m-4 cursor-pointer"
          onClick={() => router.back()}
        />
      </div>
      <div className="p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0 h-16 w-16 rounded-full bg-gray-200 overflow-hidden">
            <img className="h-full w-full object-cover" src={photoURL} alt="User avatar" />
          </div>
          <div className="ml-4">
            <h2 className="text-2xl font-bold text-gray-900">{displayName}</h2>
            <p className="text-sm text-gray-600">@{Email}</p>
          </div>
          <button onClick={handleEditToggle} className="ml-auto text-gray-600 hover:text-gray-900">
            {editMode ? <FaSave size={20} /> : <FaUserEdit size={20} />}
          </button>
        </div>
        <div className="mt-6">
          <CustomInput
            label="Name"
            value={name? name : displayName}
            onChange={(e) => setName(e.target.value)}
            disabled={!editMode}
            inputType="text"
          />
          
          <CustomInput
            label="Email"
            value={email ? email : Email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={!editMode}
            inputType="email"
          />
          <CustomInput
            label="Link"
            value={link}
            onChange={(e) => setLink(e.target.value)}
            disabled={!editMode}
            inputType="text"
          />
          <CustomInput
            label="Bio"
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            disabled={!editMode}
            inputType="text"
          />
        </div>
      </div>
    </div>
  </div>
  </ProtectedRoute>
  );
};

export default Profile;
