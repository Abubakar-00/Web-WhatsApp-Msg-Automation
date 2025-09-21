# WhatsApp Automation Scheduler

A powerful web-based WhatsApp automation tool that allows you to schedule and send WhatsApp messages programmatically. Built with FastAPI, SQLAlchemy, and Selenium for reliable message delivery.

<p align="center">
    <img width="1306" height="892" alt="image" src="https://github.com/user-attachments/assets/435c1f49-0114-4a53-9666-4d5bff5f848d" />
</p>

## 🚀 Features

### ✅ Core Functionality
- **Instant Messaging**: Send WhatsApp messages immediately to any phone number
- **Message Scheduling**: Schedule messages for future delivery at specific dates and times
- **Sequential Processing**: Messages are processed in a queue system to ensure reliable delivery
- **Persistent Login**: One-time WhatsApp Web login that persists across sessions
- **Message History**: Complete tracking of sent, failed, and pending messages
- **Real-time Dashboard**: Live updates of pending schedules and message status

### 📊 Dashboard Features
- **Statistics Overview**: Track pending messages, daily sent count, and failed deliveries
- **Pending Schedules Management**: View and cancel scheduled messages
- **Message History**: Complete log of all message attempts with timestamps and status
- **Login Management**: Easy setup and clearing of WhatsApp Web sessions

### 🔒 Security & Reliability
- **Profile-based Authentication**: Uses Chrome profiles to maintain WhatsApp Web sessions
- **Retry Mechanism**: Automatic retry for failed message deliveries
- **Error Handling**: Comprehensive error logging and screenshot capture for debugging
- **Sequential Delivery**: Prevents WhatsApp rate limiting by processing messages one at a time

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Chrome Browser
- Stable internet connection

### 1. Clone the Repository
```bash
git clone https://github.com/Abubakar-00/Web-WhatsApp-Msg-Automation.git
cd Web-WhatsApp-Msg-Automation
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

The application will start on `http://localhost:8000`

## 📱 Getting Started

### Step 1: Initial WhatsApp Login Setup
1. Open your browser and navigate to `http://localhost:8000`
2. Click the **"Setup WhatsApp Login"** button
3. A Chrome browser window will open with WhatsApp Web
4. Scan the QR code using your WhatsApp mobile app
5. Wait for the login to complete (you'll see a success message)
6. The browser will close and your session will be saved

> **Note**: This is a one-time setup. Your WhatsApp session will persist across application restarts.

### Step 2: Clear Login (When Needed)
- Click **"Clear Login Data"** if you want to:
  - Switch to a different WhatsApp account
  - Reset your session due to login issues
  - Clear stored browser data

## 🎯 How to Use

### Sending Immediate Messages
1. Fill in the phone number (include country code, e.g., 1234567890 without +)
2. Enter your message
3. Select **"Send Now"**
4. Click **"Create Schedule"**

### Scheduling Messages for Later
1. Fill in the phone number and message
2. Select **"Schedule"**
3. Choose your desired date and time
4. Click **"Create Schedule"**

### Managing Scheduled Messages
- View all pending messages in the **"Pending Schedules"** section
- Cancel any pending message by clicking the **"Cancel"** button
- Monitor real-time statistics on the dashboard

## 📋 Understanding the Queue System

### Sequential Processing
- **All messages are processed sequentially**, not in parallel
- This prevents WhatsApp from detecting automated behavior
- Ensures higher delivery success rates
- Reduces the risk of account restrictions

### Message States
- **Pending**: Message is scheduled and waiting to be sent
- **Sent**: Message delivered successfully
- **Failed**: Message delivery failed (will be retried automatically)
- **Canceled**: Message was manually canceled before sending

## 🔧 Technical Architecture

### Components
- **FastAPI**: Web framework providing REST API and web interface
- **SQLAlchemy**: Database ORM for message and schedule management
- **APScheduler**: Background job scheduler for timed message delivery
- **Selenium**: Web automation for WhatsApp Web interaction
- **SQLite**: Lightweight database for data persistence

### 📁 File Structure
```
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and connection
├── models.py           # SQLAlchemy database models
├── scheduler.py        # Background job scheduling logic
├── whatsapp_service.py # WhatsApp Web automation service
├── templates/          # HTML templates
│   └── index.html     # Main dashboard template
├── static/           # Images, Logos
├── requirements.txt    # Python dependencies
└── chrome_profiles/   # Stored Chrome profiles (auto-created)
```

## 🚨 Important Notes

### Phone Number Format
- Always include country code (e.g., 1234567890) without +
- Remove any spaces, dashes, or special characters
- Example: 923001234567 (Pakistan), 14155552671 (US)

### Message Limitations
- WhatsApp Web has rate limits to prevent spam
- The application processes messages sequentially to respect these limits
- Large message queues will take time to process completely

### Browser Requirements
- Chrome browser is required (automatically managed by the application)
- Headless mode is used for scheduled messages
- Browser window only appears during initial login setup

## 🐛 Troubleshooting

### Common Issues

**Login Not Working**
- Try clicking "Clear Login Data" and setup again
- Ensure Chrome browser is installed and updated
- Check your internet connection

**Messages Not Sending**
- Verify phone number format includes country code
- Check if WhatsApp Web works manually in your browser
- Review the message history for error details

**Scheduled Messages Not Firing**
- Ensure the application is running continuously
- Check system clock is accurate
- Verify scheduled time is in the future

### Debug Information
- Error screenshots are automatically saved as `whatsapp_error.png`
- Check console output for detailed error messages
- Message history shows status of all delivery attempts

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Please use responsibly and in accordance with WhatsApp's Terms of Service. The developers are not responsible for any misuse of this software.

## 🔗 Repository

[GitHub - Web WhatsApp Message Automation](https://github.com/Abubakar-00/Web-WhatsApp-Msg-Automation)

---

**Made with ❤️ for automated WhatsApp messaging**
