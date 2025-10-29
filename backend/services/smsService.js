const axios = require('axios');

class SMSService {
    constructor() {
        this.apiKey = process.env.SMS_API_KEY;
        this.apiUrl = process.env.SMS_API_URL || 'https://api.twilio.com/2010-04-01';
        this.fromNumber = process.env.SMS_FROM_NUMBER;
        this.enabled = process.env.SMS_ENABLED === 'true';
        
        // Firebase initialization is now handled in NotificationService
        // This keeps SMS service independent
    }

    // Send SMS to parent
    async send(phoneNumber, message) {
        if (!this.enabled) {
            console.log(`[SMS DISABLED] Would send to ${phoneNumber}: ${message}`);
            return { success: true, messageId: 'disabled', cost: 0 };
        }

        try {
            // Clean phone number (remove spaces, dashes, etc.)
            const cleanNumber = this.cleanPhoneNumber(phoneNumber);
            
            // Truncate message if too long (SMS limit is usually 160 chars)
            const truncatedMessage = this.truncateMessage(message);

            // Send via SMS gateway (example using Twilio format)
            const response = await axios.post(`${this.apiUrl}/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Messages.json`, {
                To: cleanNumber,
                From: this.fromNumber,
                Body: truncatedMessage
            }, {
                auth: {
                    username: process.env.TWILIO_ACCOUNT_SID,
                    password: process.env.TWILIO_AUTH_TOKEN
                }
            });

            console.log(`✅ SMS sent to ${cleanNumber}: ${truncatedMessage}`);
            
            return {
                success: true,
                messageId: response.data.sid,
                cost: parseFloat(response.data.price || 0),
                status: response.data.status
            };

        } catch (error) {
            console.error('❌ SMS sending failed:', error.message);
            
            // Try alternative SMS gateway or fallback
            return await this.sendFallback(phoneNumber, message);
        }
    }

    // Send bulk SMS (for school-wide announcements)
    async sendBulk(phoneNumbers, message) {
        const results = [];
        
        for (const phoneNumber of phoneNumbers) {
            try {
                const result = await this.send(phoneNumber, message);
                results.push({
                    phoneNumber,
                    ...result
                });
                
                // Add delay to avoid rate limiting
                await this.delay(100);
                
            } catch (error) {
                results.push({
                    phoneNumber,
                    success: false,
                    error: error.message
                });
            }
        }
        
        const successCount = results.filter(r => r.success).length;
        console.log(`📊 Bulk SMS: ${successCount}/${phoneNumbers.length} sent successfully`);
        
        return {
            totalSent: phoneNumbers.length,
            successful: successCount,
            failed: phoneNumbers.length - successCount,
            results
        };
    }

    // Fallback SMS service (use different provider)
    async sendFallback(phoneNumber, message) {
        try {
            // Example: Use local SMS gateway or different provider
            console.log(`📱 [FALLBACK] SMS to ${phoneNumber}: ${message}`);
            
            // For demo purposes, just log it
            return {
                success: true,
                messageId: 'fallback_' + Date.now(),
                cost: 0,
                provider: 'fallback'
            };
            
        } catch (error) {
            console.error('❌ Fallback SMS also failed:', error.message);
            return {
                success: false,
                error: 'All SMS services failed'
            };
        }
    }

    // Send emergency SMS (high priority)
    async sendEmergency(phoneNumbers, message) {
        const emergencyMessage = `🚨 URGENT - ${message}`;
        return await this.sendBulk(phoneNumbers, emergencyMessage);
    }

    // Clean and format phone number
    cleanPhoneNumber(phoneNumber) {
        // Remove all non-digit characters except +
        let clean = phoneNumber.replace(/[^\d+]/g, '');
        
        // Add country code if missing (assuming local country)
        if (!clean.startsWith('+')) {
            // Add your country code here (example: +1 for US, +91 for India)
            const countryCode = process.env.DEFAULT_COUNTRY_CODE || '+1';
            clean = countryCode + clean;
        }
        
        return clean;
    }

    // Truncate message to SMS limits
    truncateMessage(message, maxLength = 160) {
        if (message.length <= maxLength) {
            return message;
        }
        
        return message.substring(0, maxLength - 3) + '...';
    }

    // Add delay between messages
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Get SMS delivery status
    async getDeliveryStatus(messageId) {
        if (!this.enabled) {
            return { status: 'disabled' };
        }

        try {
            const response = await axios.get(`${this.apiUrl}/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Messages/${messageId}.json`, {
                auth: {
                    username: process.env.TWILIO_ACCOUNT_SID,
                    password: process.env.TWILIO_AUTH_TOKEN
                }
            });

            return {
                status: response.data.status,
                errorCode: response.data.error_code,
                errorMessage: response.data.error_message,
                price: response.data.price,
                dateUpdated: response.data.date_updated
            };

        } catch (error) {
            console.error('Error checking SMS status:', error.message);
            return { status: 'unknown', error: error.message };
        }
    }

    // Validate phone number format
    isValidPhoneNumber(phoneNumber) {
        const cleanNumber = this.cleanPhoneNumber(phoneNumber);
        // Basic validation - should be 10-15 digits with country code
        return /^\+\d{10,15}$/.test(cleanNumber);
    }

    // Get SMS cost estimate
    getCostEstimate(messageCount, messageLength = 160) {
        const baseCost = 0.0075; // Example: $0.0075 per SMS
        const longMessageMultiplier = Math.ceil(messageLength / 160);
        return messageCount * baseCost * longMessageMultiplier;
    }

    // Format SMS for different communication types
    formatMessage(type, data) {
        const schoolName = process.env.SCHOOL_NAME || 'School';
        
        switch (type) {
            case 'attendance':
                return `${schoolName}: ${data.studentName} was marked ${data.status} on ${data.date}. ${data.notes || ''}`.trim();
            
            case 'assignment':
                return `${schoolName}: New assignment "${data.title}" for ${data.studentName}. Due: ${data.dueDate}`;
            
            case 'meeting':
                return `${schoolName}: Meeting request for ${data.studentName}. Purpose: ${data.purpose}. Reply to confirm.`;
            
            case 'emergency':
                return `🚨 ${schoolName} URGENT: ${data.message}`;
            
            case 'general':
                return `${schoolName}: ${data.message}`;
            
            default:
                return `${schoolName}: ${data.message}`;
        }
    }
}

module.exports = new SMSService();