import React, { useState } from "react";
import "./PdfPopup.css";

// const REACT_APP_BACKEND_URL = process.env.REACT_APP_BACKEND_URL

function PdfPopup({ togglePdfPopup }) {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [uploadStatus, setUploadStatus] = useState("");

    const handleFileChange = (event) => {
        setSelectedFiles(Array.from(event.target.files));
        setUploadStatus("");
    };

    const handleUpload = async () => {
        if (selectedFiles.length === 0) {
            setUploadStatus("Bitte wähle eine oder mehrere Dateien aus.");
            return;
        }
    
        setUploadStatus("Hochladen und Indexierung läuft...");
    
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append("files", file));
    
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/upload-pdf`, {
                method: "POST",
                body: formData,
            });
    
            const result = await response.json();
            setUploadStatus(result.message.join("\n")); // Zeige alle Nachrichten an
        } catch (error) {
            setUploadStatus("Verbindung zum Server fehlgeschlagen.");
        }
    };

    return (
        <div className="pdf-popup">
            <h2>PDFs hochladen und indexieren</h2>
            <input type="file" accept=".pdf" multiple onChange={handleFileChange} />
            <button onClick={handleUpload}>Hochladen und indexieren</button>
            <pre>{uploadStatus}</pre>
            <button onClick={togglePdfPopup} className="close-popup">
                Schließen
            </button>
        </div>
    );
}

export default PdfPopup;
