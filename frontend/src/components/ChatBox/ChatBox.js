// ChatBox.js
import React from "react";
import "./ChatBox.css";

function ChatBox({ messages }) {
    return (
        <div className="chatbox">
            {messages.map((msg, index) => (
                <div
                    key={index}
                    className={`message ${msg.sender}-message`}
                    {...(msg.sender === "bot" && msg.isHtml
                        ? { dangerouslySetInnerHTML: { __html: msg.text } }
                        : { children: msg.text })}
                ></div>
            ))}
        </div>
    );
}

export default ChatBox;
