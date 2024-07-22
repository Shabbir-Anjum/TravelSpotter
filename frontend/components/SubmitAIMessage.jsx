import React, { useState } from "react";
import { sendAiMessage } from "@/API/Api";
import toast, { Toaster } from 'react-hot-toast';
import Recommendation from "@/components/Recommendation/Recommendation"; // Import Recommendation component

const SubmitAIMessage = ({ currentRoom, currentuser, serverUrl, setShowSubmitAIMessage }) => {
  const [outing_topic, setOutingName] = useState("");
  const [location, setAddress] = useState("");
  const [showRecommendation, setShowRecommendation] = useState(false); // State to toggle recommendation
  const[AiResponse,setAiResponse]= useState(null)
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await sendAiMessage(serverUrl, currentRoom, {
        outing_topic: outing_topic,
        location: location,
        send_from: currentuser,
      });
      setOutingName("");
      setAddress("");
      setAiResponse(response)
      toast.success("Recieved recommendation successfully!");
      setShowRecommendation(true); // Show recommendation after submitting AI message
    } catch (error) {
      console.error("Error submitting AI message:", error);
      toast.error("Error submitting AI message.");
    }
  };

  return (
    <div className="w-11/12 max-w-lg h-96 bg-white absolute z-50 left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 rounded-lg p-4 flex flex-col">
      <form onSubmit={handleSubmit} className="space-y-4 mx-auto py-24">
        <input
          type="text"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          placeholder="Enter outing name"
          value={outing_topic}
          onChange={(e) => setOutingName(e.target.value)}
        />
        <input
          type="text"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
          placeholder="Enter address (City, Country)"
          value={location}
          onChange={(e) => setAddress(e.target.value)}
        />
        <button
          type="submit"
          className="w-full p-2 bg-black text-white rounded hover:bg-green-600"
        >
          Submit
        </button>
      </form>
      {showRecommendation && <Recommendation AiResponse={AiResponse} />} {/* Show recommendation when state is true */}
      <Toaster position="top-left" />
    </div>
  );
};

export default SubmitAIMessage;
