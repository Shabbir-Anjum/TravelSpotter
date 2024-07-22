


// Function to handle fetch errors
const handleFetchErrors = (response) => {
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return response.json();
};

// Function to add a new outing
const addOuting = async (serverUrl,outingData) => {
 
  try {
    const response = await fetch(`${serverUrl}/api/add-outing`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'insomnia/9.2.0'
      },
      body: JSON.stringify({
        "name" : "Teepon5",
        "email" : "m5@teepon.com",
        "friend_emails" : {
          "1" : "m2@teepon.com",
          "2" : "m3@teepon.com",
          "3" : "m5@teepon.com"
        }
      }),
    });
    return response;
  } catch (error) {
    console.error('Error adding outing:', error);
    throw error;
  }
};

// Function to add a new user
const addUser = async (userData) => {

  try {
    const response = await fetch(`${serverUrl}/api/add-user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error adding user:', error);
    throw error;
  }
};

// Function to delete a friend by ID
const deleteFriend = async (friendId) => {

  try {
    const response = await fetch(`${serverUrl}/api/delete-friend/${friendId}`, {
      method: 'DELETE',
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error deleting friend:', error);
    throw error;
  }
};

// Function to delete an outing by ID
const deleteOuting = async (serverUrl,outingId) => {

  try {
    const response = await fetch(`${serverUrl}/api/delete-outing/${outingId}`, {
      method: 'DELETE',
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error deleting outing:', error);
    throw error;
  }
};

// Function to delete the current user
const deleteMe = async () => {

  try {
    const response = await fetch(`${serverUrl}/api/delete-me`, {
      method: 'DELETE',
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error deleting user:', error);
    throw error;
  }
};

// Function to get the list of friends
const getFriends = async (serverUrl) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-friends`, {
      method: 'GET',
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error getting friends:', error);
    throw error;
  }
};

// Function to get details of an outing by ID
const getOuting = async (outingId) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-outing/${outingId}`, {
      method: 'GET',
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error getting outing details:', error);
    throw error;
  }
};

// Function to get the list of all outings
const listOutings = async (serverUrl,email) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-outings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'insomnia/9.2.0'
      },
      body: JSON.stringify({email: email}),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error listing outings:', error);
    throw error;
  }
};

// Function to update user details
const updateMe = async (userData) => {

  try {
    const response = await fetch(`${serverUrl}/api/update-me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error updating user:', error);
    throw error;
  }
};

// Function to send a message
const SendMessage = async (messageData,currentRoom,serverUrl) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-outings/${currentRoom}/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'insomnia/9.2.0'
      },
      body: JSON.stringify(messageData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// Function to update details of an outing by ID
const updateOuting = async (outingId, outingData) => {

  try {
    const response = await fetch(`${serverUrl}/api/update-outing/${outingId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(outingData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error updating outing:', error);
    throw error;
  }
};

// Function to update details of a friend by ID
const updateFriend = async (friendId, friendData) => {

  try {
    const response = await fetch(`${serverUrl}/api/update-friend/${friendId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(friendData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error updating friend:', error);
    throw error;
  }
};

// Function to get AI messages for a specific outing
const getAiMessages = async (serverUrl,outingId) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-outing/${outingId}/ai-messages`, {
      method: 'GET',
      headers: {
        'User-Agent': 'insomnia/9.2.0', // Specify user agent if needed
      },
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error getting AI messages:', error);
    throw error;
  }
};

// Function to send a message to AI for a specific outing
const sendAiMessage = async (serverUrl,currentRoom, messageData) => {

  try {
    const response = await fetch(`${serverUrl}/api/get-outings/${currentRoom}/ai-chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'insomnia/9.2.0'
      },
      body: JSON.stringify(messageData),
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error sending AI message:', error);
    throw error;
  }
};

const getMessages = async (serverUrl,currentRoom) => {
  try {
    const response = await fetch(`${serverUrl}/api/get-outings/${currentRoom}/chat`, {
      method: 'GET',
      headers: {
        'User-Agent': 'insomnia/9.2.0'
      },
    });
    return handleFetchErrors(response);
  } catch (error) {
    console.error('Error fetching messages:', error);
    throw error;
  }
};
// Exporting all functions for use in other parts of the application
export {
  addOuting,
  addUser,
  deleteFriend,
  deleteOuting,
  deleteMe,
  getFriends,
  getOuting,
  listOutings,
  updateMe,
  SendMessage,
  updateOuting,
  updateFriend,
  getAiMessages,
  sendAiMessage,
  getMessages
};
