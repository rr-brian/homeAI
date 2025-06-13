import React from 'react';
import { Box, Container, Typography, Grid, Card, CardContent } from '@mui/material';
import { motion } from 'framer-motion';
import { Search as SearchIcon, TrendingUp as TrendingUpIcon, Description as DescriptionIcon } from '@mui/icons-material';

const Home = () => {
  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          minHeight: '500px',
          py: 6,
          display: 'flex',
          alignItems: 'center',
          background: 'linear-gradient(45deg, #1a365d 30%, #2a4a7f 90%)',
          position: 'relative',
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, maxWidth: '1100px !important', py: 4 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Grid container spacing={4}>
              {[
                {
                  icon: <SearchIcon sx={{ fontSize: 48, color: 'white' }} />,
                  title: 'Intelligent Search',
                  description: 'Advanced AI-powered search capabilities to find exactly what you need across your real estate data.',
                },
                {
                  icon: <TrendingUpIcon sx={{ fontSize: 48, color: 'white' }} />,
                  title: 'Prediction and Anomaly Detection',
                  description: 'Leverage machine learning to predict trends and identify unusual patterns in your property data.',
                },
                {
                  icon: <DescriptionIcon sx={{ fontSize: 48, color: 'white' }} />,
                  title: 'Document Management',
                  description: 'Smart document processing and organization for efficient property and contract management.',
                },
              ].map((card, index) => (
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.2 }}
                  >
                    <Card
                      elevation={0}
                      sx={{
                        height: '280px',
                        maxWidth: '300px',
                        margin: '0 auto',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        borderRadius: 2,
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        transition: 'transform 0.2s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-8px)',
                          backgroundColor: 'rgba(255, 255, 255, 0.15)',
                        },
                      }}
                    >
                      <CardContent sx={{ 
                        p: 4, 
                        textAlign: 'center',
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}>
                        <Box>
                          <Box sx={{ mb: 3 }}>
                            {card.icon}
                          </Box>
                          <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, color: 'white' }}>
                            {card.title}
                          </Typography>
                        </Box>
                        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          {card.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;