// InputBar.js
import React from "react";
import "./InputBar.css";
import { FaFilePdf } from "react-icons/fa";

function InputBar({ input, setInput, sendMessage, togglePdfPopup }) {
    return (
        <div className="input-container">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your question..."
                onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
            <button className="pdf-button" onClick={togglePdfPopup}>
                <FaFilePdf />
            </button>
        </div>
    );
}

export default InputBar;
