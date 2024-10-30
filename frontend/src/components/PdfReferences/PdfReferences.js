import React, { useState } from "react";
import "./PdfReferences.css";

function PdfReferences({ answerData }) {
    const [isLeftPopupVisible, setLeftPopupVisible] = useState(false);

    const toggleLeftPopup = () => {
        setLeftPopupVisible(!isLeftPopupVisible);
    };

    return (
        <div className="pdf-references-container">
            <button className="long-button" onClick={toggleLeftPopup}>
                Browse references
            </button>
            {isLeftPopupVisible && (
                <div className="left-popup">
                    <h3>References used</h3>
                    {answerData && answerData.used_chunks && answerData.used_chunks.length > 0 ? (
                        <ul className="chunk-list">
                            {answerData.used_chunks.map((chunk, index) => (
                                <li key={index} className="chunk-item">
                                    <h4>
                                        {chunk.file_name ? chunk.file_name : "Unknown Document"} - 
                                        Page {chunk.page_number ? chunk.page_number : "Unknown Page"}
                                    </h4>
                                    <p>{chunk.text}</p>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No references found.</p>
                    )}
                    <button className="close-popup" onClick={toggleLeftPopup}>Schließen</button>
                </div>
            )}
        </div>
    );
}

export default PdfReferences;
