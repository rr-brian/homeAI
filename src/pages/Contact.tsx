import React, { useState } from 'react';
import { Box, Container, TextField, Button, Typography, Snackbar, Paper, Alert } from '@mui/material';
import { motion } from 'framer-motion';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the form data to your backend
    console.log('Form submitted:', formData);
    setOpenSnackbar(true);
    setFormData({
      name: '',
      email: '',
      message: '',
    });
  };

  return (
    <Box sx={{ py: 8, bgcolor: '#f5f5f5', minHeight: '80vh' }}>
      <Container maxWidth="sm">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Paper elevation={0} sx={{ p: 4, bgcolor: '#fff' }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Contact Us
            </Typography>
            <Typography paragraph color="text.secondary" sx={{ mb: 3 }}>
              We'd love to hear from you. Fill out the form and we'll get back to you as soon as possible.
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mb: 3 }}>
              <TextField
                required
                fullWidth
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                sx={{ mb: 2 }}
              />
              <TextField
                required
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                sx={{ mb: 2 }}
              />
              <TextField
                required
                fullWidth
                label="Message"
                name="message"
                multiline
                rows={4}
                value={formData.message}
                onChange={handleChange}
                sx={{ mb: 2 }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
                  bgcolor: '#1a365d',
                  color: '#fff',
                  fontWeight: 600,
                  '&:hover': { bgcolor: '#00163b' },
                }}
              >
                Send Message
              </Button>
            </Box>
          </Paper>
        </motion.div>
      </Container>

      <Snackbar
          open={openSnackbar}
          autoHideDuration={6000}
          onClose={() => setOpenSnackbar(false)}
        >
          <Alert onClose={() => setOpenSnackbar(false)} severity="success" sx={{ width: '100%' }}>
            Thank you for your message. We'll get back to you soon!
          </Alert>
        </Snackbar>
    </Box>
  );
};

export default Contact;
