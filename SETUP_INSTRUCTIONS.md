# SportsVision Pro - Setup Instructions

## Quick Start (Windows)

### Option 1: Using the Start Script
1. Double-click `start.bat` to automatically start both backend and frontend servers
2. Wait for both servers to start (about 30 seconds)
3. Open your browser and go to `http://localhost:3000`

### Option 2: Manual Setup

#### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Step 2: Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Step 3: Start Backend Server
```bash
cd backend
python main.py
```

#### Step 4: Start Frontend Server (in a new terminal)
```bash
cd frontend
npm start
```

## First Time Setup

### 1. Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- Git (optional)

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# The YOLO model will be downloaded automatically on first run
# This may take a few minutes
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### 4. Start the Application
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

## Using the Application

### 1. Create an Account
- Go to `http://localhost:3000`
- Click "Sign up here" on the login page
- Fill in your details:
  - Full Name
  - Email Address
  - Phone Number
  - Password

### 2. Upload a Video
- After logging in, click "Upload Video"
- Drag and drop a video file or click to browse
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- Maximum file size: 100MB

### 3. Wait for Processing
- The AI will process your video in the background
- You can see the status on the dashboard
- Processing typically takes 1-5 minutes depending on video length

### 4. View Results
- Once processing is complete, click "View Results"
- Watch the analyzed video with:
  - Player detection and tracking
  - Ball movement tracking
  - Trajectory predictions
  - Velocity information

## Troubleshooting

### Common Issues

#### Backend Won't Start
- Make sure Python 3.9+ is installed
- Check if port 8000 is available
- Install dependencies: `pip install -r requirements.txt`

#### Frontend Won't Start
- Make sure Node.js 18+ is installed
- Check if port 3000 is available
- Install dependencies: `npm install`

#### Video Processing Fails
- Check if the video file is valid
- Ensure file size is under 100MB
- Try with a shorter video first

#### Model Download Issues
- The YOLO model downloads automatically on first run
- Ensure you have internet connection
- Check if antivirus is blocking the download

### Performance Tips

1. **For Better Results**:
   - Use videos with good lighting
   - Ensure players and ball are clearly visible
   - Avoid excessive camera movement

2. **For Faster Processing**:
   - Use shorter video clips (1-2 minutes)
   - Lower resolution videos process faster
   - Close other applications to free up memory

3. **System Requirements**:
   - At least 4GB RAM
   - 2GB free disk space
   - Modern CPU (Intel i5 or equivalent)

## File Structure

```
sports-video-analysis/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main application file
│   ├── video_processor.py  # ML video processing
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Uploaded videos (created automatically)
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── public/            # Static files
├── utils/                 # Utility functions
├── start.bat             # Windows start script
├── start.sh              # Linux/Mac start script
└── README.md             # Detailed documentation
```

## API Endpoints

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Ensure all dependencies are installed correctly
4. Try restarting both servers

## Next Steps

After successful setup:
1. Upload a test video to verify everything works
2. Explore the different features and settings
3. Check the API documentation for advanced usage
4. Customize the application for your specific needs

Enjoy using SportsVision Pro! 🏆
