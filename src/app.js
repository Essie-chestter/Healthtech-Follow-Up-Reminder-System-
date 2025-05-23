import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [patientName, setPatientName] = useState('');
    const [appointmentTime, setAppointmentTime] = useState('');
    const [contactNumber, setContactNumber] = useState('');
    const [whatsappNumber, setWhatsappNumber] = useState('');
    const [emailAddress, setEmailAddress] = useState('');
    const [preferredChannel, setPreferredChannel] = useState('sms');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        try {
            const response = await axios.post('/.netlify/functions/appointment_scheduler/schedule', {
                patient_name: patientName,
                appointment_time: appointmentTime,
                contact_number: contactNumber,
                whatsapp_number: whatsappNumber,
                email_address: emailAddress,
                preferred_channel: preferredChannel
            });

            setMessage(response.data.message);
            setPatientName('');
            setAppointmentTime('');
            setContactNumber('');
            setWhatsappNumber('');
            setEmailAddress('');
            setPreferredChannel('sms');
        } catch (err) {
            setError(err.response ? err.response.data.message : err.message);
        }
    };

    return (
        <div className="container">
            <h1>Schedule Appointment</h1>
            {error && <div className="error">{error}</div>}
            {message && <div className="success">{message}</div>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="patientName">Patient Name:</label>
                    <input
                        type="text"
                        id="patientName"
                        value={patientName}
                        onChange={(e) => setPatientName(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="appointmentTime">Appointment Time (YYYY-MM-DDTHH:MM:SS):</label>
                    <input
                        type="datetime-local"
                        id="appointmentTime"
                        value={appointmentTime}
                        onChange={(e) => setAppointmentTime(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="contactNumber">Contact Number:</label>
                    <input
                        type="tel"
                        id="contactNumber"
                        value={contactNumber}
                        onChange={(e) => setContactNumber(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="whatsappNumber">WhatsApp Number:</label>
                    <input
                        type="tel"
                        id="whatsappNumber"
                        value={whatsappNumber}
                        onChange={(e) => setWhatsappNumber(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="emailAddress">Email Address:</label>
                    <input
                        type="email"
                        id="emailAddress"
                        value={emailAddress}
                        onChange={(e) => setEmailAddress(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="preferredChannel">Preferred Channel:</label>
                    <select
                        id="preferredChannel"
                        value={preferredChannel}
                        onChange={(e) => setPreferredChannel(e.target.value)}
                    >
                        <option value="sms">SMS</option>
                        <option value="whatsapp">WhatsApp</option>
                        <option value="email">Email</option>
                        <option value="voice">Voice Call</option>
                    </select>
                </div>
                <button type="submit">Schedule</button>
            </form>
        </div>
    );
}

export default App;