    import React, { useState } from "react";
    import { useNavigate } from "react-router-dom"; // Import useNavigate
    import "./LearningForm.css";
    import Navbar from "../components/Navbar/Navbar";
    import Footer from "../components/Footer/Footer";

    const LearningForm = () => {
    const navigate = useNavigate(); // Initialize navigate function

    const [formData, setFormData] = useState({
        ageGroup: "",
        educationLevel: "",
        learningGoals: "",
        courseDuration: "",
        certificationNeed: "",
        learningSpeed: "",
        attentionSpan: "",
        processingSpeed: "",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
        const response = await fetch("http://localhost:5000/submit-form", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
        });
        navigate("/");
        if (response.ok) {
            console.log("Form submitted successfully");
            // Redirect to homepage after successful submission
        } else {
            console.error("Failed to submit form");
        }
        } catch (error) {
        console.error("Error submitting form:", error);
        }
    };

    return (
        <>
        <Navbar />
        <div className="c-space align-middle justify-center items-center" style={{ marginLeft: "30%" }}>
            <div className="contact-container">
            <h2 className="head-text">Learning Preferences Form</h2>
            <form onSubmit={handleSubmit}>
                <label className="field-label">Age Group:</label>
                <select className="field-input" name="ageGroup" value={formData.ageGroup} onChange={handleChange}>
                <option value="">Select</option>
                <option value="10-12">10-12</option>
                <option value="13-14">13-14</option>
                <option value="15-18">15-18</option>
                <option value="18+">18+</option>
                </select>

                <label className="field-label">Education Level:</label>
                <select className="field-input" name="educationLevel" value={formData.educationLevel} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Primary School">Primary School</option>
                <option value="Middle School">Middle School</option>
                <option value="High School">High School</option>
                <option value="College">College</option>
                <option value="Professional">Professional</option>
                </select>

                <label className="field-label">Learning Goals:</label>
                <select className="field-input" name="learningGoals" value={formData.learningGoals} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Exam Preparation">Exam Preparation</option>
                <option value="Skill Development">Skill Development</option>
                <option value="Career Growth">Career Growth</option>
                <option value="Hobby Learning">Hobby Learning</option>
                </select>

                <label className="field-label">Course Duration:</label>
                <select className="field-input" name="courseDuration" value={formData.courseDuration} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Short">Short (1-4 weeks)</option>
                <option value="Medium">Medium (1-3 months)</option>
                <option value="Long">Long (3+ months)</option>
                </select>

                <label className="field-label">Certification Need:</label>
                <select className="field-input" name="certificationNeed" value={formData.certificationNeed} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
                </select>

                <label className="field-label">Learning Speed:</label>
                <select className="field-input" name="learningSpeed" value={formData.learningSpeed} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Fast Learner">Fast Learner</option>
                <option value="Moderate Pace Learner">Moderate Pace Learner</option>
                <option value="Prefers Step-by-Step">Prefers Step-by-Step</option>
                </select>

                <label className="field-label">Attention Span & Focus:</label>
                <select className="field-input" name="attentionSpan" value={formData.attentionSpan} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Highly Focused">Highly Focused</option>
                <option value="Easily Distracted">Easily Distracted</option>
                <option value="Prefers Short Lessons">Prefers Short Lessons</option>
                </select>

                <label className="field-label">Processing Speed & Learning Adaptability:</label>
                <select className="field-input" name="processingSpeed" value={formData.processingSpeed} onChange={handleChange}>
                <option value="">Select</option>
                <option value="Slow but Accurate Learner">Slow but Accurate Learner</option>
                <option value="Quick but Error-Prone Learner">Quick but Error-Prone Learner</option>
                <option value="Adjusts Quickly to New Formats">Adjusts Quickly to New Formats</option>
                <option value="Needs Predictable Learning Structure">Needs Predictable Learning Structure</option>
                </select>

                <button className="field-btn mt-6" type="submit">
                Submit
                </button>
            </form>
            </div>
        </div>
        <Footer />
        </>
    );
    };

    export default LearningForm;
