const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const twilio = require('twilio');
const fetch = require('node-fetch');

const PORT = process.env.PORT || 6000;
const API_URL = process.env.API_URL || 'http://api:3000';
const AUTH_URL = process.env.AUTH_URL || 'http://auth:4000';
const TWILIO_SID = process.env.TWILIO_SID;
const TWILIO_TOKEN = process.env.TWILIO_TOKEN;
const TWILIO_PHONE = process.env.TWILIO_PHONE;

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize Twilio client if credentials provided
const twilioClient = TWILIO_SID && TWILIO_TOKEN ? twilio(TWILIO_SID, TWILIO_TOKEN) : null;

// Simple session store for SMS conversations
const smsessions = new Map(); // phoneNumber -> { state, userData, lastActivity }

app.get('/health', (req, res) => res.json({ status: 'ok' }));

// USSD Menu System
const USSD_MENU = {
  main: {
    text: "Welcome to SchoolBridge\n1. Check Messages\n2. Send Message\n3. My Profile\n0. Exit",
    options: { '1': 'check_messages', '2': 'send_message', '3': 'profile', '0': 'exit' }
  },
  check_messages: {
    text: "Recent Messages:\n[Would fetch from API]\n0. Back to main menu",
    options: { '0': 'main' }
  },
  send_message: {
    text: "Enter recipient phone number:",
    next: 'send_message_content'
  },
  send_message_content: {
    text: "Enter your message:",
    next: 'send_message_confirm'
  }
};

// USSD Handler
app.post('/ussd', (req, res) => {
  const { sessionId, phoneNumber, text } = req.body;
  
  let session = smsessions.get(phoneNumber) || { state: 'main', userData: {} };
  session.lastActivity = new Date();
  
  let response = '';
  let continueSession = true;

  try {
    if (!text) {
      // First request
      response = USSD_MENU.main.text;
      session.state = 'main';
    } else {
      const currentMenu = USSD_MENU[session.state];
      
      if (session.state === 'main') {
        const nextState = currentMenu.options[text];
        if (nextState === 'exit') {
          response = "Thank you for using SchoolBridge!";
          continueSession = false;
        } else if (nextState && USSD_MENU[nextState]) {
          session.state = nextState;
          response = USSD_MENU[nextState].text;
        } else {
          response = "Invalid option. " + USSD_MENU.main.text;
        }
      } else if (session.state === 'send_message') {
        session.userData.recipient = text;
        session.state = 'send_message_content';
        response = USSD_MENU.send_message_content.text;
      } else if (session.state === 'send_message_content') {
        session.userData.message = text;
        response = `Send "${text}" to ${session.userData.recipient}?\n1. Yes\n2. No`;
        session.state = 'send_message_confirm';
      } else if (session.state === 'send_message_confirm') {
        if (text === '1') {
          // Would integrate with API to send message
          response = "Message sent successfully!\n0. Back to main menu";
          session.state = 'main';
        } else {
          response = USSD_MENU.main.text;
          session.state = 'main';
        }
      } else {
        // Handle going back
        if (text === '0' && currentMenu.options && currentMenu.options['0']) {
          session.state = currentMenu.options['0'];
          response = USSD_MENU[session.state].text;
        } else {
          response = USSD_MENU.main.text;
          session.state = 'main';
        }
      }
    }
  } catch (error) {
    response = "Service temporarily unavailable. Please try again.";
    continueSession = false;
  }

  smsessions.set(phoneNumber, session);
  
  // USSD response format (depends on provider)
  res.type('text/plain').send(continueSession ? `CON ${response}` : `END ${response}`);
});

// SMS Handler (Twilio webhook)
app.post('/sms', async (req, res) => {
  const { From, Body } = req.body;
  const phoneNumber = From;
  const message = Body.trim();

  try {
    let responseText = '';

    // Simple SMS command parsing
    if (message.toLowerCase().startsWith('login')) {
      const parts = message.split(' ');
      if (parts.length >= 3) {
        const [, username, password] = parts;
        // Attempt login via auth service
        const loginResponse = await fetch(`${AUTH_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        
        if (loginResponse.ok) {
          const data = await loginResponse.json();
          // Store session for this phone number
          smsessions.set(phoneNumber, { 
            state: 'authenticated', 
            token: data.token, 
            username,
            lastActivity: new Date() 
          });
          responseText = `Welcome ${username}! You are now logged in. Send 'MESSAGES' to check messages or 'HELP' for commands.`;
        } else {
          responseText = "Login failed. Please check your username and password.";
        }
      } else {
        responseText = "Usage: LOGIN username password";
      }
    } else if (message.toLowerCase() === 'messages') {
      const session = smsessions.get(phoneNumber);
      if (session && session.token) {
        responseText = "Recent messages: [Would fetch from API with token]\n\nSend 'HELP' for more commands.";
      } else {
        responseText = "Please login first. Send: LOGIN username password";
      }
    } else if (message.toLowerCase() === 'help') {
      responseText = "SchoolBridge SMS Commands:\nLOGIN username password\nMESSAGES - Check messages\nHELP - This help\n\nFor full features, use USSD or web app.";
    } else {
      responseText = "Unknown command. Send 'HELP' for available commands or 'LOGIN username password' to start.";
    }

    // Send SMS response if Twilio is configured
    if (twilioClient && TWILIO_PHONE) {
      await twilioClient.messages.create({
        body: responseText,
        from: TWILIO_PHONE,
        to: phoneNumber
      });
    } else {
      console.log(`SMS Response to ${phoneNumber}: ${responseText}`);
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('SMS processing error:', error);
    res.status(500).send('Error');
  }
});

// Send SMS (for other services to use)
app.post('/send-sms', async (req, res) => {
  const { to, message } = req.body;
  
  if (!twilioClient || !TWILIO_PHONE) {
    return res.status(500).json({ error: 'SMS not configured' });
  }

  try {
    const result = await twilioClient.messages.create({
      body: message,
      from: TWILIO_PHONE,
      to: to
    });
    res.json({ success: true, messageId: result.sid });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`SMS/USSD Gateway running on ${PORT}`);
  if (twilioClient) {
    console.log('Twilio integration enabled');
  } else {
    console.log('Twilio not configured - SMS responses will be logged only');
  }
});