// App.js
import React, { useState } from "react";
import "./App.css";
import ChatBox from "./components/ChatBox/ChatBox";
import InputBar from "./components/InputBar/InputBar";
import PdfPopup from "./components/PdfPopup/PdfPopup";
import PdfReferences from "./components/PdfReferences/PdfReferences";
import CorrectAnswer from "./components/CorrectAnswer/CorrectAnswer";

const apiUrl = "http://127.0.0.1:8000/ask";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [answerData, setAnswerData] = useState(null);
    const [isPdfPopupVisible, setPdfPopupVisible] = useState(false);

    const sendMessage = async () => {
        if (input.trim() === "") return;

        const userMessage = { text: input, sender: "user" };
        setMessages([...messages, userMessage]);

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: input }),
            });
            const data = await response.json();

            const botMessage = {
                text: data.answer || `Error: ${data.error}`,
                sender: "bot",
                isHtml: true,
            };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
            setAnswerData(data);
        } catch (error) {
            setMessages((prevMessages) => [
                ...prevMessages,
                { text: "Error connecting to server.", sender: "bot" },
            ]);
        }

        setInput("");
    };

    const togglePdfPopup = () => {
        setPdfPopupVisible(!isPdfPopupVisible);
    };

    return (
        <div className="chat-container">
            <h1>AI Chatbot</h1>
            <ChatBox messages={messages} />
            <InputBar
                input={input}
                setInput={setInput}
                sendMessage={sendMessage}
                togglePdfPopup={togglePdfPopup}
            />
            <PdfReferences answerData={answerData} />
            <CorrectAnswer />
            {isPdfPopupVisible && <PdfPopup messages={messages} togglePdfPopup={togglePdfPopup} />}
        </div>
    );
}

export default App;