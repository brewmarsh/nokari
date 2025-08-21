import React from 'react';

const JobFilters = ({
  filtersVisible,
  setFiltersVisible,
  title,
  setTitle,
  company,
  setCompany,
  search,
  setSearch,
}) => {
  return (
    <div>
      <button onClick={() => setFiltersVisible(!filtersVisible)}>
        {filtersVisible ? 'Hide Filters' : 'Show Filters'}
      </button>
      {filtersVisible && (
        <div>
          <input
            type="text"
            placeholder="Filter by title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            type="text"
            placeholder="Filter by company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          />
          <input
            type="text"
            placeholder="Search by keyword"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      )}
    </div>
  );
};

export default JobFilters;
