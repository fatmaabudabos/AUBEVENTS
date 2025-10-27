import React from "react";
import { useNavigate } from "react-router-dom";
import { Calendar, Users, MapPin, Star } from "lucide-react";
import "./Landing.css";

export default function Landing() {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: <Calendar className="feature-icon" />,
      title: "Discover Events",
      description: "Find workshops, lectures, concerts, and club activities happening around campus"
    },
    {
      icon: <Users className="feature-icon" />,
      title: "Easy Registration",
      description: "Register for events with just one click and manage your schedule effortlessly"
    },
    {
      icon: <MapPin className="feature-icon" />,
      title: "Campus-Wide",
      description: "Events from all departments, clubs, and organizations across AUB"
    },
    {
      icon: <Star className="feature-icon" />,
      title: "Stay Updated",
      description: "Never miss out on exciting opportunities and experiences at AUB"
    }
  ];
  
  return (
    <div className="landing-container">
      <div className="landing-hero">
        <div className="hero-content">
          <h1 className="hero-title">AUBEVENTS</h1>
          <p className="hero-subtitle">
            Your gateway to campus life at the American University of Beirut
          </p>
          <p className="hero-description">
            Discover workshops, lectures, concerts, club fairs, and more. 
            Connect with your community and make the most of your university experience.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary large" onClick={() => navigate("/signup")}>
              Get Started
            </button>
            <button className="btn btn-outline large" onClick={() => navigate("/login")}>
              Sign In
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-card">
            <Calendar size={24} />
            <span>Upcoming Events</span>
          </div>
          <div className="floating-card delay-1">
            <Users size={24} />
            <span>Join Community</span>
          </div>
          <div className="floating-card delay-2">
            <Star size={24} />
            <span>Campus Life</span>
          </div>
        </div>
      </div>
      
      <div className="features-section">
        <div className="features-container">
          <h2 className="features-title">Why Choose AUBEVENTS?</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                {feature.icon}
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
