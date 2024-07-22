'use client';

import { useState } from 'react';
import { useSignInWithEmailAndPassword } from 'react-firebase-hooks/auth';
import { auth, googleProvider } from '@/services/firebase/config';
import { useRouter } from 'next/navigation';
import { FcGoogle } from 'react-icons/fc';
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { useSelector } from "react-redux";
const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [signInWithEmailAndPassword, user, loading, error] = useSignInWithEmailAndPassword(auth);
  const router = useRouter();
  const serverUrl = useSelector((state) => state.chat.server_url);
  const handleGoogleSignIn = async () => {
    try {
      const provider = new GoogleAuthProvider();
      provider.addScope('https://www.googleapis.com/auth/calendar.events.readonly');
      const res = await signInWithPopup(auth, provider);

      if (res) {
        const credential = GoogleAuthProvider.credentialFromResult(res);
        const access_token = credential.accessToken;
        const refreshToken = res.user.refreshToken; // Get the refresh token
        const name = res.user.displayName;
        const email = res.user.email;

    

        // Send token and user details to backend
        await sendUserDetailsToBackend(name, email, access_token, refreshToken);

        sessionStorage.setItem('user', true);
        sessionStorage.setItem('accessToken', access_token); // Store the access token

        router.push('/');
      } else {
        console.error('Google authentication failed');
      }
    } catch (e) {
      console.error('Google sign-in error:', e);
    }
  };
const sendUserDetailsToBackend = async (name, email, access_token, refreshToken) => {
    try {
      const response = await fetch(`${serverUrl}/api/add-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
           'User-Agent': 'insomnia/9.2.0'
        },
        body: JSON.stringify({
          name: name,
          email: email,
          access_token: access_token,
          refresh_token: refreshToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
     
      } else {
        console.error('Failed to add user:', response.statusText);
      
      }
    } catch (error) {
      console.error('Error sending user details to backend:', error);
    }
  };
 
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-10 rounded-lg shadow-xl w-96">
        <h1 className="text-white text-3xl mb-5 font-semibold text-center tracking-wider font-sans ">
          Sign In
        </h1>
        {error && <p className="text-red-500 mb-5">{error.message}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 mb-4 bg-gray-700 rounded outline-none text-white placeholder-gray-500"
        />
        <div className='flex gap-4 mb-4 '>
          <button
            onClick={handleGoogleSignIn}
            className="w-full p-3 bg-indigo-600 rounded text-white hover:bg-indigo-500"
          >
            Sign In
          </button>
        </div>
        <button
          onClick={handleGoogleSignIn}
          className="w-full p-3 bg-white rounded text-gray-700 hover:bg-gray-200 flex items-center justify-center gap-2"
        >
          <FcGoogle size={24} />
          Sign in with Google
        </button>
      </div>
    </div>
  );
};

export default SignIn;
