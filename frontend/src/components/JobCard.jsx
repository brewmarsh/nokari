import React from 'react';
import PinIcon from './PinIcon.jsx';
import ThreeDotsIcon from './icons/ThreeDotsIcon.jsx';
import HideIcon from './icons/HideIcon.jsx';

const Badge = ({ location }) => {
    const badgeStyle = {
      padding: '4px 8px',
      borderRadius: '12px',
      color: 'white',
      fontSize: '0.8rem',
      fontWeight: 'bold',
      marginRight: '5px',
      textTransform: 'capitalize',
    };

    const badgeColors = {
      remote: 'var(--secondary-green)',
      hybrid: 'var(--primary-blue)',
      onsite: 'var(--neutral-gray)',
    };

    const style = {
      ...badgeStyle,
      backgroundColor: badgeColors[location.type],
    };

    return <span style={style}>{location.type}</span>;
};

const JobCard = ({ job, openMenu, setOpenMenu, handlePin, handleHide, handleHideCompany, handleFindSimilar }) => {
  return (
    <div className={`job-card ${job.is_pinned ? 'pinned' : ''}`}>
      <div className="job-card-left">
        <div className="job-card-header">
          <h2 className="job-title">
            <a href={job.link} target="_blank" rel="noopener noreferrer">{job.title}</a>
          </h2>
        </div>
        <p className="company-name">{job.company}</p>
        {job.locations && job.locations.length > 0 && (
          <div className="job-location">
            {job.locations.map((loc, index) => (
              <span key={index}>{loc.location_string}</span>
            ))}
          </div>
        )}
        <p className="posting-date">
          Posted on: {new Date(job.posting_date).toLocaleDateString()}
        </p>
        <p className="description">{job.description}</p>
      </div>
      <div className="job-card-right">
        <div className="job-card-actions">
          <button onClick={() => handlePin(job.link, job.is_pinned)} title={job.is_pinned ? 'Unpin Job' : 'Pin Job'} className="pin-icon">
            <PinIcon isPinned={job.is_pinned} />
          </button>
          <div className="action-menu">
            <button onClick={() => setOpenMenu(openMenu === job.link ? null : job.link)} className="three-dots-icon">
              <ThreeDotsIcon />
            </button>
            {openMenu === job.link && (
              <div className="dropdown-menu">
                <button onClick={() => { handleHide(job.link); setOpenMenu(null); }}>Hide Job</button>
                <button onClick={() => { handleHideCompany(job.company); setOpenMenu(null); }}>Hide Company</button>
                <button onClick={() => handleFindSimilar(job)}>Find similar</button>
              </div>
            )}
          </div>
        </div>
        <div className="job-card-badges">
          {job.locations && job.locations.map((loc, index) => (
            <Badge key={index} location={loc} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default JobCard;
