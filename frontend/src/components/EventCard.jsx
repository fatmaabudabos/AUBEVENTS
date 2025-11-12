import { useEffect, useState } from 'react';
import { MapPin, Users, Clock, CheckCircle, Plus } from 'lucide-react';
import './EventCard.css';

function EventCard({ event, isRegistered, onRegister, onUnregister }) {
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    setImageError(false);
  }, [event.image_url]);

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`event-card ${isRegistered ? 'registered' : ''}`}>
      {event.image_url && !imageError && (
        <div className="event-image-wrapper">
          <img
            src={event.image_url}
            alt={`${event.title || 'Event'} poster`}
            className="event-image"
            onError={() => setImageError(true)}
          />
        </div>
      )}
      <div className="event-header">
        <h3>{event.title}</h3>
        {isRegistered && <CheckCircle className="registered-badge" size={20} />}
      </div>

      {event.description && (
        <p className="event-description">{event.description}</p>
      )}

      <div className="event-details">
        {event.time && (
          <div className="detail">
            <Clock size={16} />
            <span>{formatDate(event.time)}</span>
          </div>
        )}
        {event.location && (
          <div className="detail">
            <MapPin size={16} />
            <span>{event.location}</span>
          </div>
        )}
        {typeof event.capacity === 'number' && (
          <div className="detail">
            <Users size={16} />
            <span>Capacity: {event.capacity}</span>
          </div>
        )}
        {event.organizers && event.organizers.length > 0 && (
          <div className="detail">
            <Users size={16} />
            <span>Organizers: {event.organizers.join(', ')}</span>
          </div>
        )}
      </div>

      <div className="event-actions">
        {isRegistered ? (
          <button
            onClick={() => onUnregister(event.id)}
            className="btn btn-secondary"
          >
            Unregister
          </button>
        ) : (
          <button
            onClick={() => onRegister(event.id)}
            className="btn btn-primary"
          >
            <Plus size={16} />
            Register
          </button>
        )}
      </div>
    </div>
  );
}

export default EventCard;