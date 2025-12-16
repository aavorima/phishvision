# Twilio SMS Integration Setup Guide

This guide will help you set up Twilio SMS integration for PhishVision's smishing (SMS phishing) campaigns.

## 📱 What is Twilio?

Twilio is a cloud communications platform that allows you to send and receive SMS messages programmatically. PhishVision uses Twilio to send simulated phishing SMS messages for security awareness training.

## 🚀 Quick Setup

### Step 1: Create a Twilio Account

1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a **free trial account**
   - Trial accounts get $15.00 credit
   - Can send SMS to verified phone numbers
3. Verify your email and phone number

### Step 2: Get Your Twilio Credentials

After signing up, you'll need three pieces of information:

1. **Account SID**
   - Found on your [Twilio Console Dashboard](https://console.twilio.com)
   - Looks like: `AC1234567890abcdef1234567890abcdef`

2. **Auth Token**
   - Click "Show" next to Auth Token on the dashboard
   - Looks like: `1234567890abcdef1234567890abcdef`

3. **Twilio Phone Number**
   - Click "Get a Trial Number" on the dashboard
   - Format: `+12345678900` (E.164 format)

### Step 3: Configure PhishVision

You have two options to configure Twilio in PhishVision:

#### Option A: Environment Variables (Recommended for Testing)

Add these to your `.env` file in the backend directory:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+12345678900
```

#### Option B: User Settings (Recommended for Production)

1. Log into PhishVision
2. Go to **Settings** page
3. Scroll to **Twilio SMS Configuration**
4. Enter your:
   - Twilio Account SID
   - Twilio Auth Token
   - Twilio Phone Number
5. Click **Save**

### Step 4: Install Twilio Library

```bash
cd backend
pip install twilio
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### Step 5: Restart Backend

```bash
python app.py
```

## ✅ Testing Your Setup

### Test 1: Send a Test SMS

Use the API to send a test message:

```bash
POST http://localhost:5000/api/sms/test
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "message": "This is a test SMS from PhishVision"
}
```

Or use curl:

```bash
curl -X POST http://localhost:5000/api/sms/test \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+1234567890", "message":"Test from PhishVision"}'
```

### Test 2: Validate a Phone Number

```bash
POST http://localhost:5000/api/sms/validate-phone
Content-Type: application/json

{
  "phone_number": "+1234567890"
}
```

### Test 3: Send an SMS Campaign

1. Go to **SMS Campaigns** in PhishVision
2. Create a new SMS campaign
3. Add target phone numbers
4. Click "Send Campaign"
5. Check that SMS messages are delivered

## 📋 Trial Account Limitations

**Important:** Twilio trial accounts have restrictions:

### Restrictions:
- ❌ Can only send SMS to **verified phone numbers**
- ❌ All messages include "Sent from your Twilio trial account" prefix
- ❌ **Cannot use alphanumeric sender IDs** (company names like "Birbank", "Umico", etc.)
- ❌ Can only send from your Twilio phone number (e.g., +18166436401)
- ✅ $15.00 credit (~500 SMS messages in the US)
- ✅ Perfect for testing and demos

### To Verify Phone Numbers (Trial Only):

1. Go to [Phone Numbers > Verified Caller IDs](https://console.twilio.com/us1/develop/phone-numbers/manage/verified)
2. Click "Add new number"
3. Enter the phone number you want to send test messages to
4. Complete the verification code

### Upgrade to Remove Restrictions:

1. Go to your [Twilio Console](https://console.twilio.com)
2. Click "Upgrade" in the top banner
3. Add billing information
4. After upgrade:
   - ✅ Send to any phone number (no verification needed)
   - ✅ No "trial account" prefix in messages
   - ✅ **Use alphanumeric sender IDs** (company names work!)
   - ✅ Send from custom sender IDs like "Birbank", "Umico", etc.
   - ✅ Pay-as-you-go pricing (~$0.0079/SMS in US)

## 💰 Pricing (After Trial)

| Service | Cost (US) |
|---------|-----------|
| SMS Sending | $0.0079 per message |
| Phone Number (Monthly) | $1.15 per month |
| Lookup API (validation) | $0.005 per lookup |

**Example:** 1,000 SMS messages = ~$7.90 + $1.15/month

## 📱 Phone Number Format

Phone numbers MUST be in **E.164 format**:

✅ Correct:
- `+12025551234` (US)
- `+442071234567` (UK)
- `+61412345678` (Australia)

❌ Incorrect:
- `(202) 555-1234`
- `202-555-1234`
- `12025551234` (missing +)

The Twilio service will auto-format US numbers for you.

## 🏢 Custom Sender ID (Alphanumeric Sender ID)

PhishVision supports **custom sender IDs** for SMS campaigns, allowing messages to appear from company names instead of phone numbers.

⚠️ **REQUIRES UPGRADED TWILIO ACCOUNT** - Alphanumeric sender IDs do NOT work on trial accounts. See "Upgrade to Remove Restrictions" above.

### Features:
- **Company Name Display**: SMS appears from "Birbank", "Umico", "Kapital" instead of +1234567890
- **Regional Support**: Works in Azerbaijan and many other countries
- **Built-in Presets**: Quick selection of Azerbaijan companies (Birbank, Umico, Kapital Bank, Bakcell, Azercell, etc.)
- **Custom Phone Numbers**: Use Azerbaijan numbers (+994XX XXX XX XX)
- **Flexible Options**: Company name, phone number, or custom text

### How to Use:

When creating an SMS campaign in PhishVision:

1. Choose **Sender Type**:
   - **Company Name**: Select from preset Azerbaijan companies
   - **Phone Number**: Use Azerbaijan phone number format (+994XX)
   - **Custom**: Enter any alphanumeric sender (max 11 characters)

2. **Examples**:
   ```
   Company Name: Birbank
   SMS appears from: "Birbank"

   Phone Number: +99412 345 67 89
   SMS appears from: "+99412 345 67 89"

   Custom: IT-Support
   SMS appears from: "IT-Support"
   ```

### Important Notes:

⚠️ **Regional Restrictions**:
- ✅ **Works in**: Azerbaijan, Turkey, Europe, Asia, Middle East
- ❌ **NOT supported in**: USA, Canada (requires phone number)
- Check [Twilio's country support](https://support.twilio.com/hc/en-us/articles/223133767-International-support-for-Alphanumeric-Sender-ID) for full list

⚠️ **Alphanumeric Sender ID Rules**:
- Maximum **11 characters**
- Letters and numbers only (a-z, A-Z, 0-9)
- No special characters except hyphen (-)
- Cannot be all numbers (use phone format instead)

⚠️ **Carrier Registration**:
- Some countries require pre-registration of sender IDs
- Azerbaijan generally allows alphanumeric IDs without registration
- If messages fail, check with Twilio support

### Testing Alphanumeric Sender ID:

```bash
POST http://localhost:5000/api/sms/test
Content-Type: application/json

{
  "phone_number": "+994501234567",
  "message": "Test SMS from PhishVision",
  "sender_id": "Birbank"
}
```

### Preset Azerbaijan Companies:

PhishVision includes these popular Azerbaijan companies:
- **Birbank** - Leading digital bank
- **Umico** - E-commerce platform
- **Kapital Bank** / **KapitalBank** - Major bank
- **Bakcell** - Mobile operator
- **Azercell** - Mobile operator
- **Nar Mobile** - Mobile operator
- **Azericard** - Payment system
- **ABB** - Azerbaijan Banks Association
- **Pasha Bank** - Banking institution

## 🔒 Security Best Practices

1. **Never commit credentials to git**
   - Use `.env` files (already in `.gitignore`)
   - Or use user settings in database

2. **Rotate credentials regularly**
   - Generate new auth tokens every 90 days
   - Available in Twilio Console > Settings > API Keys

3. **Use separate accounts**
   - Production account
   - Development/testing account

4. **Monitor usage**
   - Check [Twilio usage dashboard](https://console.twilio.com/us1/monitor/usage)
   - Set up billing alerts

## 🎯 SMS Campaign Workflow

### 1. Create Campaign
```javascript
POST /api/sms/campaigns
{
  "name": "Q1 Security Test - Package Delivery",
  "description": "Test employee awareness of delivery scams",
  "message_template": "Your package could not be delivered. Reschedule: {{link}}",
  "sender_id": "FedEx"
}
```

### 2. Add Targets
```javascript
POST /api/sms/campaigns/{campaign_id}/targets
{
  "targets": [
    {"phone_number": "+12025551001", "email": "user1@company.com"},
    {"phone_number": "+12025551002", "email": "user2@company.com"}
  ]
}
```

### 3. Send Campaign
```javascript
POST /api/sms/campaigns/{campaign_id}/send
{}
```

### 4. Track Results
```javascript
GET /api/sms/campaigns/{campaign_id}/stats
```

## 📊 Features Available

| Feature | Description |
|---------|-------------|
| **Bulk SMS Sending** | Send to multiple recipients in one API call |
| **Click Tracking** | Track when users click SMS links |
| **Delivery Status** | Know if SMS was delivered successfully |
| **Phone Validation** | Verify phone numbers before sending |
| **Landing Pages** | Redirect to credential harvesting pages |
| **Training Pages** | Redirect to security awareness training |
| **Templates** | Pre-built smishing templates |
| **Statistics** | Campaign analytics and click rates |

## 🛠️ Troubleshooting

### Error: "Twilio credentials not configured"

**Solution:** Make sure you've set:
- Environment variables in `.env`, OR
- User settings in PhishVision Settings page

### Error: "The number +1234567890 is unverified"

**Solution:** You're using a trial account. Either:
- Verify the phone number in Twilio Console, OR
- Upgrade your Twilio account

### Error: "Unable to create record: The 'To' number +1234567890 is not a valid phone number"

**Solution:** Use E.164 format (e.g., `+12025551234`)

### SMS not delivered

**Possible causes:**
1. Invalid phone number format
2. Phone number is blocked
3. Carrier filtering (rare)
4. Twilio account suspended (check console)

**Check:**
- Go to [Twilio Logs](https://console.twilio.com/us1/monitor/logs/sms)
- Look for error messages
- Verify phone number format

### "Warning: Twilio library not installed"

**Solution:**
```bash
pip install twilio
```

## 📚 API Reference

### Send Test SMS
```
POST /api/sms/test
{
  "phone_number": "+12025551234",
  "message": "Test message"
}
```

### Validate Phone
```
POST /api/sms/validate-phone
{
  "phone_number": "+12025551234"
}
```

### Get SMS Templates
```
GET /api/sms/templates
```

### Get Campaign Stats
```
GET /api/sms/campaigns/{id}/stats
```

## 🔗 Useful Links

- [Twilio Console](https://console.twilio.com)
- [Twilio SMS Quickstart](https://www.twilio.com/docs/sms/quickstart/python)
- [Twilio Pricing](https://www.twilio.com/sms/pricing/us)
- [Twilio Support](https://support.twilio.com)

## ✨ Demo Mode

If Twilio is not configured, PhishVision runs in **mock mode**:
- ✅ Campaigns are created normally
- ✅ Targets are added
- ✅ "Send" marks messages as sent
- ❌ No actual SMS is sent
- 📝 Messages are logged to console

Perfect for testing the UI without spending credits!

## 🎓 Next Steps

1. ✅ Set up Twilio account
2. ✅ Configure credentials
3. ✅ Send test SMS
4. ✅ Create your first campaign
5. ✅ Add targets
6. ✅ Send and track results
7. ✅ Review analytics

Happy smishing (ethically)! 📱🔒
