import React, { useState, useCallback, useEffect, useRef } from 'react';
import '../utils/grid-setup';
import { Box, Container, TextField, Button, Typography, CircularProgress, Paper } from '@mui/material';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { motion } from 'framer-motion';

interface SearchResult {
  content: string;
  filename: string;
  metadata_storage_name: string;
  [key: string]: any;
}

const Search: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [rowData, setRowData] = useState<SearchResult[]>([]);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true,
  };

  const columnDefs: ColDef<SearchResult>[] = [
  {
    headerName: 'File Name',
    field: 'metadata_storage_name',
    flex: 1,
    sortable: true,
    filter: true,
    resizable: true,
  },
  {
    headerName: 'Content',
    field: 'content',
    flex: 3,
    autoHeight: true,
    wrapText: true,
    cellStyle: { whiteSpace: 'normal' },
    sortable: true,
    filter: true,
    resizable: true,
  },
];

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      console.log('Sending search request:', searchQuery);
      const response = await fetch('http://127.0.0.1:8000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error('Search request failed');
      }

      const data = await response.json();
      console.log('Search response:', data);
      // AG Grid expects an array of rows, each with metadata_storage_name and content fields
      // The backend returns an array of objects with these fields at the top level
      setRowData(Array.isArray(data) ? data : data.results || []);
      setSummary(data.summary || '');

      // Update search history
      setSearchHistory(prev => {
        const newHistory = [searchQuery, ...prev.filter(q => q !== searchQuery)].slice(0, 10);
        localStorage.setItem('searchHistory', JSON.stringify(newHistory));
        return newHistory;
      });
    } catch (error) {
      console.error('Search error:', error);
      if (error instanceof Error) {
        setSummary(`Error: ${error.message}`);
      } else {
        setSummary('An unknown error occurred');
      }
      setSummary('Error performing search. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  // Load search history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === 'Enter' && document.activeElement === searchInputRef.current) {
        handleSearch();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleSearch]);

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Contract - Cognitive Search AI
        </Typography>
        
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              inputRef={searchInputRef}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter your search query... (Press '/' to focus)"
              variant="outlined"
              inputProps={{
                maxLength: 1000,
                list: 'searchHistory'
              }}
            />
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={loading}
            >
              Search
            </Button>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Press <kbd>/</kbd> to focus search | Press <kbd>Enter</kbd> to search
            </Typography>
            <Button size="small" variant="outlined" onClick={clearHistory}>
              Clear History
            </Button>
          </Box>

          <datalist id="searchHistory">
            {searchHistory.map((query, index) => (
              <option key={index} value={query} />
            ))}
          </datalist>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {summary && (
          <Paper sx={{ p: 2, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Key Points
            </Typography>
            <Typography variant="body1">
              {summary}
            </Typography>
          </Paper>
        )}

        <div className="ag-theme-alpine" style={{ height: '500px', width: '100%', marginBottom: '2rem' }}>
          <AgGridReact
            rowData={rowData}
            columnDefs={columnDefs}
            pagination={true}
            paginationPageSize={10}
            defaultColDef={defaultColDef}
            animateRows={true}
            enableCellTextSelection={true}
            suppressRowClickSelection={true}
            theme="legacy"
            paginationPageSizeSelector={[10, 20, 50, 100]}
          />
        </div>
      </Container>
    </motion.div>
  );
};

export default Search;
