# Base64 to Image/GIF Converter API

A FastAPI-based REST API that converts base64 encoded images to GIF files and various image formats with customizable parameters.

## Features

- Convert single or multiple base64 images to GIF
- Convert single base64 image to various formats (PNG, JPEG, BMP, TIFF, WebP)
- Customizable width and height
- Transparency support
- Animation support with multiple images
- Configurable loop count and frame duration
- Automatic image format detection and conversion
- Aspect ratio preservation for single image conversion
- JPEG quality control

## Installation

### Option 1: Docker Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd base64toGif
```

2. Build and run with Docker:
```bash
# Build the image
docker build -t base64-converter-api .

# Run the container
docker run -d -p 8000:8000 --name base64-converter-api base64-converter-api
```

### Option 2: Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd base64toGif
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### Endpoints

- `GET /` - API information
- `POST /convert-gif` - Convert base64 images to GIF
- `POST /convert-image` - Convert base64 image to various formats
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Convert GIF Endpoint

**URL:** `POST /convert-gif`

**Request Body:**
```json
{
  "base64Images": ["base64_string_1", "base64_string_2"],
  "width": 256,
  "height": 256,
  "transparent": false,
  "loop": 0,
  "duration": 100
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base64Images` | Array[string] | Yes | - | List of base64 encoded image strings |
| `width` | integer | No | 256 | Width of the output GIF |
| `height` | integer | No | 256 | Height of the output GIF |
| `transparent` | boolean | No | false | Enable transparency |
| `loop` | integer | No | 0 | Number of loops (0 for infinite) |
| `duration` | integer | No | 100 | Duration between frames in milliseconds |

**Response:**
- Returns a GIF file as attachment
- Content-Type: `image/gif`

### Convert Image Endpoint

**URL:** `POST /convert-image`

**Request Body:**
```json
{
  "base64Image": "base64_string",
  "width": 256,
  "height": 256,
  "format": "PNG",
  "quality": 95
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `base64Image` | string | Yes | - | Base64 encoded image string |
| `width` | integer | No | - | Width of the output image (maintains aspect ratio if only width specified) |
| `height` | integer | No | - | Height of the output image (maintains aspect ratio if only height specified) |
| `format` | string | No | "PNG" | Output format (PNG, JPEG, BMP, TIFF, WebP) |
| `quality` | integer | No | 95 | JPEG quality (1-100, only applies to JPEG format) |

**Response:**
- Returns an image file as attachment
- Content-Type varies based on format (`image/png`, `image/jpeg`, etc.)

## Usage Examples

### Python Example

```python
import requests
import base64

# Read image files and convert to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Convert images to base64
image1_base64 = image_to_base64("image1.png")
image2_base64 = image_to_base64("image2.jpg")

# API request
url = "http://localhost:8000/convert-gif"
payload = {
    "base64Images": [image1_base64, image2_base64],
    "width": 512,
    "height": 512,
    "transparent": True,
    "loop": 3,
    "duration": 200
}

response = requests.post(url, json=payload)

# Save the GIF
if response.status_code == 200:
    with open("output.gif", "wb") as f:
        f.write(response.content)
    print("GIF created successfully!")
else:
    print(f"Error: {response.json()}")
```

### JavaScript Example

```javascript
// Convert image to base64
function imageToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Convert to GIF
async function convertToGif(imageFiles) {
    const base64Images = await Promise.all(
        Array.from(imageFiles).map(file => imageToBase64(file))
    );

    const response = await fetch('http://localhost:8000/convert-gif', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            base64Images: base64Images,
            width: 512,
            height: 512,
            transparent: false,
            loop: 0,
            duration: 150
        })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Download the GIF
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted.gif';
        a.click();
    } else {
        const error = await response.json();
        console.error('Error:', error);
    }
}

// Convert to Image
async function convertToImage(imageFile, format = 'PNG') {
    const base64Image = await imageToBase64(imageFile);

    const response = await fetch('http://localhost:8000/convert-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            base64Image: base64Image,
            width: 512,
            height: 512,
            format: format,
            quality: 90
        })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Download the image
        const a = document.createElement('a');
        a.href = url;
        a.download = `converted.${format.toLowerCase()}`;
        a.click();
    } else {
        const error = await response.json();
        console.error('Error:', error);
    }
}
```

### cURL Examples

**Convert to GIF:**
```bash
curl -X POST "http://localhost:8000/convert-gif" \
  -H "Content-Type: application/json" \
  -d '{
    "base64Images": ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="],
    "width": 256,
    "height": 256,
    "transparent": false,
    "loop": 0,
    "duration": 100
  }' \
  --output output.gif
```

**Convert to PNG:**
```bash
curl -X POST "http://localhost:8000/convert-image" \
  -H "Content-Type: application/json" \
  -d '{
    "base64Image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "width": 256,
    "height": 256,
    "format": "PNG"
  }' \
  --output output.png
```

**Convert to JPEG:**
```bash
curl -X POST "http://localhost:8000/convert-image" \
  -H "Content-Type: application/json" \
  -d '{
    "base64Image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "width": 512,
    "format": "JPEG",
    "quality": 90
  }' \
  --output output.jpg
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters or base64 data)
- `500` - Internal Server Error

Error responses include a `detail` field with the error message.

## Supported Image Formats

### Input Formats
The API can handle various input image formats:
- PNG
- JPEG/JPG
- GIF
- BMP
- TIFF
- WebP

### Output Formats
- **GIF endpoint** (`/convert-gif`): Always outputs GIF format
- **Image endpoint** (`/convert-image`): Supports PNG, JPEG, BMP, TIFF, WebP formats

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

### Building the Image

```bash
docker build -t base64-converter-api .
```

### Running the Container

```bash
docker run -d -p 8000:8000 --name base64-converter-api base64-converter-api
```

### Container Management

```bash
# View logs
docker logs base64-converter-api

# Stop the container
docker stop base64-converter-api

# Remove the container
docker rm base64-converter-api

# Restart the container
docker restart base64-converter-api
```

### Environment Variables

You can customize the deployment by setting environment variables:

```bash
docker run -d -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  -e MAX_WORKERS=4 \
  -e LOG_LEVEL=info \
  --name base64-converter-api \
  base64-converter-api
```

## Production Deployment

For production deployment, consider:

1. **Reverse Proxy**: Use Nginx or Apache as a reverse proxy
2. **SSL/TLS**: Enable HTTPS with Let's Encrypt
3. **Load Balancer**: Use multiple instances behind a load balancer
4. **Monitoring**: Add Prometheus/Grafana for monitoring
5. **Logging**: Configure centralized logging

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## License

MIT License 