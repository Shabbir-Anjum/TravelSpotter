// src/services/socketService.js
import { io } from 'socket.io-client';
import store from '../store/store';
import { addMessage, setSocketId } from '../store/ChatSlice';

let socket;

export const connectSocket = () => {
  socket = io('https://socket-service-4jt9.onrender.com');

  socket.on('connect', () => {
  
    store.dispatch(setSocketId(socket.id)); // Set socket ID in Redux
  });

  socket.on('receive-message', (data) => {
   store.dispatch(addMessage(data)); // Add received message to Redux
   
});

  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
   
  }
};

export const joinRoom = (roomName) => {
  if (socket) {
    socket.emit('join-room', roomName);
  
  }
};

export const sendMessage = (content, room, sender, datetime) => {
  if (socket) {
    socket.emit('message', {content, room, sender, datetime });
    
  }
};
