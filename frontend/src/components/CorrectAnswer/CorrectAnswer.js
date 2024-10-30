import React, { useState } from "react";
import "./CorrectAnswer.css";

function CorrectAnswer() {
    const [isLeftPopupVisible, setLeftPopupVisible] = useState(false);

    const toggleLeftPopup = () => {
        setLeftPopupVisible(!isLeftPopupVisible);
    };

    return (
        <div className="pdf-references-container">
            <button className="long-button" onClick={toggleLeftPopup}>
                Correct answer
            </button>
            {isLeftPopupVisible && (
                <div className="left-popup">
                    {/* Inhalt des Popups */}
                </div>
            )}
        </div>
    );
}

export default CorrectAnswer;
