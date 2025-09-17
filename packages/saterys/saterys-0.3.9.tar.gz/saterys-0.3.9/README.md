<div align="center">

# 🛰️ SATERYS

### Scalable Analysis Toolkit for Earth Remote sYStemS

[![PyPI version](https://img.shields.io/pypi/v/saterys.svg?style=for-the-badge&color=brightgreen)](https://pypi.org/project/saterys/)
[![Python versions](https://img.shields.io/pypi/pyversions/saterys.svg?style=for-the-badge&color=blue)](https://pypi.org/project/saterys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/bastian6666/saterys/ci.yml?style=for-the-badge&label=build&color=purple)](https://github.com/bastian6666/saterys/actions)

**A modern geospatial pipeline builder with interactive node-based workflows**

[📖 Documentation](#-documentation) • [🚀 Quick Start](#-quick-start) • [🎯 Examples](#-examples) • [🧩 Plugins](#-creating-plugins)

</div>

---

## 🌟 Overview

**SATERYS** is a powerful geospatial analysis platform that combines the best of modern web technologies with robust geospatial processing capabilities. Build complex Earth observation workflows using an intuitive drag-and-drop interface, execute Python-based analysis nodes, and visualize results on interactive maps.

![SATERYS Interface](https://github.com/user-attachments/assets/cbe778d1-39d9-49b0-a5f8-c26594e2aa5b)

## ✨ Key Features

<table>
<tr>
<td>

### 🎨 **Visual Pipeline Builder**
- Interactive node-based canvas powered by [Svelvet](https://svelvet.io/)
- Drag-and-drop workflow creation
- Real-time connection validation
- Dark/Light theme support

</td>
<td>

### ⚡ **High-Performance Backend**
- FastAPI-powered REST API
- Asynchronous processing
- Hot-reloadable plugin system
- Automatic error handling

</td>
</tr>
<tr>
<td>

### 🛰️ **Geospatial Native**
- Built-in support for GeoTIFF, COG, and more
- Interactive map preview with Leaflet
- Tile-based raster visualization via [rio-tiler](https://github.com/cogeotiff/rio-tiler)
- Coordinate system handling

</td>
<td>

### 🔌 **Extensible Architecture**
- Plugin-based node system
- Custom analysis functions
- Easy integration with existing tools
- Modular design patterns

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
# Install SATERYS
pip install saterys
# Verify installation
saterys --help
```

### Launch the Application

```bash
# Start SATERYS server
saterys

# Access the web interface at http://localhost:8000
```

The application will automatically:
- 🔍 Discover all available plugins
- 🌐 Start the FastAPI backend 
- 🎨 Serve the Svelte frontend
- 📊 Open your default browser

### Development Mode

For development with hot-reload:

```bash
# Start with auto-reload
saterys --dev
```

---

## 🎯 Examples

### Basic Workflow: Hello World

1. **Add a Node**: Click "Add Node" and select "hello"
2. **Configure**: Set the name parameter to "SATERYS"  
3. **Execute**: Click the "Run" button
4. **View Results**: Check the output in the logs panel

```python
# This runs automatically when you execute the hello node
def run(args, inputs, context):
    name = args.get("name", "world")
    return {"text": f"hello {name}"}
```

### Geospatial Workflow: NDVI Calculation

Create a vegetation index from satellite imagery:

```bash
# 1. Add a raster input node
# 2. Set path to your multispectral image (e.g., Landsat, Sentinel)
# 3. Add NDVI calculation node
# 4. Configure band indices (e.g., red=4, nir=5 for Landsat 8)
# 5. Connect nodes and execute
```

**Example NDVI Node Configuration:**
```json
{
  "red_band": 4,
  "nir_band": 5,
  "output_path": "./results/ndvi_output.tif",
  "dtype": "float32"
}
```

### Custom Processing with Script Node

Write inline Python for custom analysis:

```python
# Script node example - band math
import numpy as np
import rasterio

def process_raster(input_raster):
    with rasterio.open(input_raster["path"]) as src:
        # Read bands
        red = src.read(4).astype(float)
        nir = src.read(5).astype(float)
        
        # Custom vegetation index
        evi = 2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))
        
        return {"custom_index": evi}
```

---

## 📚 Documentation

### Built-in Nodes

| Node Type | Description | Use Case |
|-----------|-------------|----------|
| 🔢 **raster.input** | Load GeoTIFF/COG files | Data ingestion |
| 🌿 **raster.ndvi** | Calculate NDVI | Vegetation analysis |
| 🌊 **raster.ndwi** | Calculate NDWI | Water body detection |
| 📊 **raster.pca** | Principal Component Analysis | Dimensionality reduction |
| ➕ **sum** | Sum numeric values | Basic arithmetic |
| 👋 **hello** | Hello world example | Testing/demos |
| 📝 **script** | Custom Python code | Flexible processing |

### API Endpoints

The FastAPI backend provides REST endpoints for integration:

```bash
# Get available node types
GET /node_types

# Execute a node
POST /run_node
{
  "nodeId": "unique-id",
  "type": "raster.ndvi", 
  "args": {"red_band": 4, "nir_band": 5},
  "inputs": {...}
}

# Register raster for preview
POST /preview/register
{
  "id": "my-raster",
  "path": "/path/to/file.tif"
}

# Get map tiles
GET /preview/tile/{id}/{z}/{x}/{y}.png
```

---

## 🧩 Creating Plugins

SATERYS uses a simple plugin architecture. Create custom nodes by adding Python files to a `nodes/` directory:

### Basic Plugin Structure

```python
# nodes/my_custom_node.py

NAME = "my.custom.node"  # Unique identifier
DEFAULT_ARGS = {         # Default configuration
    "param1": "default_value",
    "param2": 42
}

def run(args, inputs, context):
    """
    Execute the node logic
    
    Args:
        args: Node configuration parameters
        inputs: Data from connected upstream nodes  
        context: Runtime context (nodeId, etc.)
        
    Returns:
        Dictionary with output data
    """
    # Your processing logic here
    result = process_data(args, inputs)
    
    return {
        "type": "custom",
        "data": result,
        "metadata": {...}
    }
```

### Raster Processing Plugin Example

```python
# nodes/custom_filter.py

NAME = "raster.custom_filter"
DEFAULT_ARGS = {
    "filter_size": 3,
    "operation": "gaussian"
}

def run(args, inputs, context):
    import rasterio
    import numpy as np
    from scipy import ndimage
    
    # Get input raster
    raster_input = next(
        (inp for inp in inputs.values() 
         if inp.get("type") == "raster"), 
        None
    )
    
    if not raster_input:
        raise ValueError("No raster input found")
    
    # Process the raster
    with rasterio.open(raster_input["path"]) as src:
        data = src.read(1)
        
        # Apply filter
        if args["operation"] == "gaussian":
            filtered = ndimage.gaussian_filter(
                data, 
                sigma=args["filter_size"]
            )
        
        # Save result...
        output_path = "/tmp/filtered_result.tif"
        # ... saving logic here ...
        
    return {
        "type": "raster",
        "path": output_path,
        "operation": "custom_filter"
    }
```

### Plugin Discovery

SATERYS automatically discovers plugins from:
1. **Built-in nodes**: `saterys/nodes/` (package installation)
2. **User nodes**: `./nodes/` (current working directory)

Simply restart the application after adding new plugins!

---

## 🛠️ Advanced Usage

### Environment Configuration

```bash
# Custom host and port
export SATERYS_HOST=0.0.0.0  
export SATERYS_PORT=8080

# Raster cache directory
export RASTER_CACHE=./my_cache

# Development frontend origin (for CORS)
export SATERYS_DEV_ORIGIN=http://localhost:5173
```

### Docker Usage

```dockerfile
FROM python:3.10-slim

RUN pip install saterys

# Add your custom nodes
COPY nodes/ /app/nodes/

WORKDIR /app

EXPOSE 8000

CMD ["saterys", "--host", "0.0.0.0"]
```

### Programmatic Usage

```python
import uvicorn
from saterys.app import app

# Customize the FastAPI app
@app.get("/custom")  
def custom_endpoint():
    return {"message": "Custom endpoint"}

# Run programmatically
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/bastian6666/SATERYS.git
cd SATERYS

# Install in development mode
pip install -e .

# Install frontend dependencies (if modifying UI)
cd saterys/web
npm install

# Start development server
npm run dev
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible  
- Add docstrings for public functions
- Test your changes before submitting

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[FastAPI](https://fastapi.tiangolo.com/)**: For building modern, high-performance APIs with ease.
- **[Uvicorn](https://www.uvicorn.org/)**: An ASGI server for lightning-fast application deployment.
- **[Pydantic](https://docs.pydantic.dev/)**: Ensuring data validation and management is smooth and reliable.
- **[NumPy](https://numpy.org/)**: The foundation for numerical computing in Python.
- **[rio-tiler](https://github.com/cogeotiff/rio-tiler)**: Efficient raster tiling and preview generation.
- **[Rasterio](https://rasterio.readthedocs.io/)**: Simplifying geospatial raster data I/O.
- **[Fiona](https://fiona.readthedocs.io/)**: A powerful library for vector data handling (GPKG/SHP).
- **[PyProj](https://pyproj4.github.io/pyproj/)**: For seamless coordinate reference system transformations.
- **[Shapely](https://shapely.readthedocs.io/)**: Geometry manipulation made easy.
- **[APScheduler](https://apscheduler.readthedocs.io/)**: A flexible scheduling library for background jobs.
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: The go-to library for database interaction and ORM functionality.
- **[pytz](https://pytz.sourceforge.net/)**: Comprehensive timezone support.
- **[tzlocal](https://github.com/regebro/tzlocal)**: Simplifies local timezone detection.

---

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/bastian6666/SATERYS/issues)
- 💬 [Discussions](https://github.com/bastian6666/SATERYS/discussions)
- 📧 [Email](mailto:bastian@example.com)

---

<div align="center">

**Made with ❤️ for the geospatial community**

[![GitHub stars](https://img.shields.io/github/stars/bastian6666/SATERYS?style=social)](https://github.com/bastian6666/SATERYS/stargazers)
[![Twitter Follow](https://img.shields.io/twitter/follow/YourTwitter?style=social)](https://twitter.com/YourTwitter)

</div>
