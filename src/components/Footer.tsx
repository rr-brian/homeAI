import React from 'react';
import { Box, Container, Grid, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box component="footer" sx={{ bgcolor: '#f5f5f5', pt: 1, pb: 2, mt: 'auto' }}>
      <Container maxWidth="lg" sx={{ pt: 0 }}>
        <Grid container spacing={2}>
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Des Moines Office
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <Link href="https://goo.gl/maps/oerp7b6d5sUnvitA6" color="inherit" target="_blank" rel="noopener">
                1080 Jordan Creek Parkway, Suite 200 North
                <br />
                West Des Moines, IA 50266
              </Link>
              <br />
              Phone: (515) 223-4500
              <br />
              Fax: (515) 223-7235
            </Typography>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Omaha Office
            </Typography>
            <Typography variant="body2" color="text.secondary">
              18881 West Dodge Road, Suite 100 West
              <br />
              Omaha, NE 68022
              <br />
              Phone: (402) 885-4002
              <br />
              Fax: (515) 223-7235
            </Typography>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Press Inquiries
            </Typography>
            <Typography variant="body2" color="text.secondary">
              For any press inquiries or media usage questions,
              <br />
              please contact Paul Rupprecht at
              <br />
              <Link href="mailto:Rupprecht.Paul@RRRealty.com" color="inherit">
                Rupprecht.Paul@RRRealty.com
              </Link>
            </Typography>
          </Grid>
        </Grid>
        
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          © 2025 R&R Realty. All rights reserved.
          <br />
          R&R Real Estate Advisors, Inc. is a licensed real estate broker in the state of Iowa.
          <br />
          R&R Realty Group, LC is a licensed real estate broker in the state of Nebraska.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
