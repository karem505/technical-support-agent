# Screen Sharing Feature

This document explains how screen sharing works in the Odoo Technical Support Agent.

## Overview

The agent supports real-time screen sharing, allowing users to show their Odoo interface to the AI support agent for visual troubleshooting and guidance.

## How It Works

### Backend (Agent)

The LiveKit agent is configured to:

1. **Enable Video Input**: The agent connects with `video_enabled=True` to receive video streams
2. **Register Byte Stream Handler**: Listens for incoming screen capture data
3. **Process Frames**: Automatically resizes and compresses images to 1024x1024 max resolution
4. **Track Subscription**: Subscribes to participant video tracks for screen share detection

#### Image Processing Pipeline

```python
async def _handle_screen_capture(self, reader: rtc.ByteStreamReader):
    # 1. Read image bytes asynchronously
    image_bytes = bytearray()
    async for chunk in reader:
        image_bytes += chunk

    # 2. Convert to PIL Image
    image = Image.open(BytesIO(image_bytes))

    # 3. Resize if needed (max 1024x1024)
    if image.width > 1024 or image.height > 1024:
        ratio = min(1024 / image.width, 1024 / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    # 4. Convert to base64 PNG
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 5. Add to chat context for AI analysis
    image_content = ImageContent(image=f"data:image/png;base64,{image_base64}")
```

### Frontend (UI)

The React frontend provides:

1. **Screen Share Button**: Toggles screen sharing on/off
2. **Visual Indicators**: Shows when screen sharing is active
3. **LiveKit Integration**: Uses LiveKit's screen share API
4. **Permission Handling**: Requests and manages browser screen capture permissions

#### Screen Share Controls

```typescript
const startScreenShare = async () => {
  await localParticipant.setScreenShareEnabled(true, {
    audio: false,           // No audio from screen
    contentHint: 'detail',  // Optimize for text clarity
    resolution: {
      width: 1920,
      height: 1080,
      frameRate: 5,         // 5 FPS for efficiency
    },
  });
};
```

## Features

### ✅ Supported

- **Full Screen Sharing**: Share entire screen or specific window
- **Automatic Resizing**: Images optimized for AI processing
- **Real-time Processing**: Frames processed as they arrive
- **Visual Feedback**: Clear UI indicators for sharing status
- **Permission Management**: Browser permission requests handled gracefully
- **Error Handling**: Graceful fallbacks for permission denials

### 📋 Frame Rate

- **5 FPS** during screen sharing (configurable)
- Optimized for technical support scenarios
- Balance between responsiveness and bandwidth

### 🎯 Resolution

- **Max 1024x1024** pixels for AI processing
- **1920x1080** captured from browser
- Aspect ratio preserved during resize

## Usage

### For Users

1. **Start Voice Session**: Click "Start Voice Session"
2. **Enable Screen Sharing**: Click "Share Screen" button
3. **Select Screen/Window**: Choose what to share from browser dialog
4. **Agent Sees Screen**: AI agent can now analyze what's displayed
5. **Stop When Done**: Click "Stop Sharing" button

### Browser Permissions

Screen sharing requires browser permissions:

- **Chrome/Edge**: `navigator.mediaDevices.getDisplayMedia()`
- **Firefox**: Same API, may show different UI
- **Safari**: Supported in Safari 13+

### Security Considerations

1. **User Consent**: Browser always asks for permission
2. **Indicator Always Visible**: Browser shows recording indicator
3. **User Can Stop Anytime**: Via button or browser controls
4. **No Background Recording**: Only when explicitly started

## Technical Details

### Supported Browsers

| Browser | Version | Notes |
|---------|---------|-------|
| Chrome | 72+ | Full support |
| Edge | 79+ | Full support |
| Firefox | 66+ | Full support |
| Safari | 13+ | Full support |
| Opera | 60+ | Full support |

### Performance

- **Bandwidth**: ~50-200 KB/s at 5 FPS
- **CPU**: Minimal impact with hardware encoding
- **Memory**: ~10-20 MB for processing

### Limitations

1. **No Audio**: Screen audio is not captured (voice only)
2. **Frame Rate**: Limited to 5 FPS for efficiency
3. **Protected Content**: Some DRM content may be blocked by browser
4. **Mobile**: Limited support on mobile browsers

## Configuration

### Backend Configuration

In `backend/agent/agent.py`:

```python
# Enable video for screen sharing
await ctx.connect(
    room_input_options=RoomInputOptions(
        video_enabled=True,
        noise_cancellation=noise_cancellation.BVC(),
    )
)

# Configure byte stream handler
ctx.room.register_byte_stream_handler(
    "screen_capture",
    lambda reader: asyncio.create_task(self._handle_screen_capture(reader))
)
```

### Frontend Configuration

In `frontend/components/VoiceAgent.tsx`:

```typescript
<LiveKitRoom
  token={token}
  serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
  connect={true}
  audio={true}
  video={true}  // Enable video for screen sharing
  onDisconnected={disconnect}
>
```

### Adjusting Frame Rate

To change the frame rate, modify the resolution settings:

```typescript
resolution: {
  width: 1920,
  height: 1080,
  frameRate: 10,  // Change from 5 to 10 FPS
}
```

### Adjusting Max Resolution

To change the max image size sent to AI:

```python
# In backend/agent/agent.py
max_size = 1536  # Change from 1024 to 1536
if image.width > max_size or image.height > max_size:
    ratio = min(max_size / image.width, max_size / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
```

## AI Vision Analysis

When screen sharing is active, the AI agent can:

1. **Identify UI Elements**: Recognize Odoo modules, menus, forms
2. **Read Error Messages**: Extract and analyze error text
3. **Spot Configuration Issues**: Notice incorrect settings
4. **Guide Navigation**: Provide step-by-step visual guidance
5. **Detect Problems**: Identify UI issues or bugs

### Example Interactions

**User**: "I'm getting an error, let me share my screen"
*[Starts screen sharing]*

**Agent**: "I can see your screen now. You have a validation error on the Sales Order form. The 'Customer' field is required but empty. Please select a customer from the dropdown."

**User**: "Where do I find the inventory settings?"
*[Shares screen]*

**Agent**: "I can see you're on the home page. Click on the 'Inventory' app icon, then go to Configuration > Settings in the top menu."

## Troubleshooting

### Screen Sharing Not Starting

**Problem**: "Failed to start screen sharing"

**Solutions**:
- Check browser permissions
- Reload the page and try again
- Ensure you're using HTTPS (required for screen capture)
- Try a different browser

### Agent Not Responding to Screen

**Problem**: Agent doesn't acknowledge screen content

**Solutions**:
- Check agent logs for image processing errors
- Verify video track is being published
- Ensure backend has `video_enabled=True`
- Check network connectivity

### Low Quality Screen Share

**Problem**: Screen appears blurry or pixelated

**Solutions**:
- Increase frame rate (but increases bandwidth)
- Adjust resolution settings
- Check network bandwidth
- Use wired connection instead of Wi-Fi

### Permission Denied

**Problem**: Browser blocks screen sharing permission

**Solutions**:
- Check browser settings for site permissions
- Clear browser data and try again
- Use incognito/private mode to test
- Check for browser extensions blocking access

## Advanced Features

### Custom Frame Sampling

Implement intelligent frame sampling based on activity:

```python
async def _handle_screen_capture(self, reader: rtc.ByteStreamReader):
    # Only process frames when agent is listening or thinking
    if self.agent_state in ['listening', 'thinking']:
        # Process frame
        pass
    else:
        # Skip frame to save bandwidth
        pass
```

### Image Comparison

Compare frames to detect changes:

```python
import imagehash

previous_hash = None

def has_significant_change(image):
    global previous_hash
    current_hash = imagehash.average_hash(image)

    if previous_hash is None:
        previous_hash = current_hash
        return True

    difference = current_hash - previous_hash
    previous_hash = current_hash

    return difference > 5  # Threshold for change detection
```

### OCR Integration

Add text extraction from screens:

```python
import pytesseract

def extract_text_from_screen(image):
    """Extract text from screen capture"""
    text = pytesseract.image_to_string(image)
    return text
```

## Future Enhancements

Planned improvements:

1. **Automatic Frame Selection**: AI decides when to capture frames
2. **Region of Interest**: Focus on specific screen areas
3. **Multi-Monitor Support**: Handle multiple displays
4. **Recording**: Save screen share sessions for review
5. **Annotations**: Allow agent to draw on screen
6. **Mobile Support**: Better mobile screen sharing

## Resources

- LiveKit Screen Share Docs: https://docs.livekit.io/guides/screen-share/
- WebRTC Screen Capture API: https://developer.mozilla.org/en-US/docs/Web/API/Screen_Capture_API
- PIL Image Processing: https://pillow.readthedocs.io/

## Support

For issues with screen sharing:

1. Check browser console for errors
2. Review backend logs for processing issues
3. Test with different screen sources
4. Report issues with browser/OS details
