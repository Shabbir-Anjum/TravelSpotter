// src/store/chatSlice.js
import { createSlice } from "@reduxjs/toolkit";


const initialState = {
  messages: [],
  currentRoom: "",
  RoomName:'',
  socketId: "",
  user: null,
  server_url: "https://teepon-backend.onrender.com/",
  userdata:null
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action) => {
      const { content, sender, datetime } = action.payload;
      state.messages.push({ content: content,
        datetime:datetime, send_from: sender });
      
    
    },
    setCurrentRoom: (state, action) => {
      state.currentRoom = action.payload;
    },
    setRoomName: (state, action) => {
      state.RoomName = action.payload;
    },
    setCurrentMessages: (state, action) => {
      state.messages = action.payload;
   
    },
    setSocketId: (state, action) => {
      state.socketId = action.payload;
    },
    setUser: (state, action) => {
      state.user = action.payload;
   
    },
    clearUser: (state) => {
      state.user = null;
    },
    setUserdata: (state, action) => {
      state.userdata = action.payload;
     
    },
  },
});

export const { addMessage,setUserdata, setCurrentRoom, setSocketId, setUser, clearUser, setCurrentMessages, server_url,setRoomName } =
  chatSlice.actions;

export default chatSlice.reducer;
