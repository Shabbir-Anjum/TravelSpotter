'use client'
import { useState } from 'react';
import { useCreateUserWithEmailAndPassword } from 'react-firebase-hooks/auth';
import { auth } from '@/services/firebase/config';
import { useRouter } from 'next/navigation';
import { AiFillEye, AiFillEyeInvisible } from 'react-icons/ai'; // Import icons for password visibility toggle
import { useDispatch } from 'react-redux';
import { setUser } from '@/store/ChatSlice'; // Adjust path as needed

const SignUp = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [createUserWithEmailAndPassword] = useCreateUserWithEmailAndPassword(auth);
  const router = useRouter();
  const [passwordVisible, setPasswordVisible] = useState(false); // State to toggle password visibility
  const dispatch = useDispatch(); // Get the dispatch function from Redux

  const validateEmail = (email) => {
    return email.endsWith('@gmail.com');
  };

  const handleSignUp = async () => {
    if (!username) {
      setError('Please enter your username.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!validateEmail(email)) {
      setError('Email must end with @gmail.com.');
      return;
    }
    setError('');
    try {
      const res = await createUserWithEmailAndPassword(email, password);
      console.log('from sigup',{ res });
     
      sessionStorage.setItem('user', true);
      dispatch(setUser(username)); // Store user information including username to Redux
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setUsername('');
      router.push('/');
    } catch (e) {
      if (e.code === 'auth/email-already-in-use') {
        setError('Email is already registered. Please enter another email.');
      } else {
        setError(e.message);
      }
      console.error(e);
    }
  };

  const togglePasswordVisibility = () => {
    setPasswordVisible(!passwordVisible);
  };
console.log('from input',username)
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-10 rounded-lg shadow-xl w-96">
        <h1 className="text-white text-2xl mb-5">Sign Up</h1>
        {error && <p className="text-red-500 mb-5">{error}</p>}
        <input 
          type="text" 
          placeholder="Username" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
          className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
        />
        <input 
          type="email" 
          placeholder="Email" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
        />
        <div className="relative">
          <input 
            type={passwordVisible ? 'text' : 'password'} 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
          />
          <div 
            className="absolute text-white text-2xl top-3 right-3 cursor-pointer"
            onClick={togglePasswordVisibility}
          >
            {passwordVisible ? <AiFillEyeInvisible className="text-gray-400" /> : <AiFillEye className="text-gray-400" />}
          </div>
        </div>
        <input 
          type={passwordVisible ? 'text' : 'password'} 
          placeholder="Confirm Password" 
          value={confirmPassword} 
          onChange={(e) => setConfirmPassword(e.target.value)} 
          className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
        />
        <div className='flex gap-4'>
          <button 
            onClick={handleSignUp}
            className="w-full p-3 bg-indigo-600 rounded text-white hover:bg-indigo-500"
          >
            Sign Up
          </button>
          <button 
            onClick={() => router.push('/sign-in')}
            className="w-full p-3 bg-indigo-600 rounded text-white hover:bg-indigo-500"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
