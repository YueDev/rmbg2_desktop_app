# RMBG-2.0 Desktop App (Image Background Removal Tool)

This is a local macOS desktop application for image background removal (matting) built with `customtkinter` and `ONNXRuntime`. It utilizes the RMBG-2.0 model to provide fully local model execution and leverages CoreML for inference acceleration on compatible hardware.

## Development Environment

(Adhering to `.rules` guidelines) All system development and debugging operations must be completed within the specified `conda` runtime environment. Please ensure that environment dependencies are up-to-date first.

```bash
# Initialize or update the environment
conda env update -n rmbg2_desktop_app -f environment.yml

# Activate the environment
conda activate rmbg2_desktop_app
```

## Running the Application

Download fp16 onnx model from https://huggingface.co/briaai/RMBG-2.0, put it into models/rmbg20_model_fp16.onnx.

The project includes a script that can detect the current conda environment and launch the application proactively. You can run it directly by double-clicking it in Finder:

```bash
./start.command
```

If you prefer to run it manually, use the following command:

```bash
python main.py
```

## Application Packaging (macOS `.app` and `.dmg`)

The current project uses `PyInstaller` to generate the executable file and resource collection, and utilizes macOS's built-in `hdiutil` to package them.

> **Note:** All packaging commands must be executed while the `rmbg2_desktop_app` conda environment is activated.

### 1. Build the application into an `.app` bundle

Run the following command:

```bash
pyinstaller --noconfirm \
  --name "RMBG2" \
  --windowed \
  --add-data "models:models" \
  --collect-all customtkinter \
  --icon "icons.icns" \
  main.py
```

*After execution is complete, the application bundle structure `RMBG2.app` will be automatically generated in the `dist/` folder in the current directory. You can double-click `RMBG2.app` here directly to test if it works.*

### 2. Package into a directly distributable `.dmg` installer (with "Drag to Applications" shortcut)

To provide a graphical interface for "drag-and-drop installation" when double-clicking the installer, we will use a temporary build folder to place the application bundle and a symbolic link to the Applications folder:

```bash
# 1. Create a temporary folder for packaging and copy the application
mkdir -p build_dmg
cp -r dist/RMBG2.app build_dmg/

# 2. Create a shortcut pointing to the system's /Applications inside the temporary folder
ln -s /Applications build_dmg/Applications

# 3. Use hdiutil to build the final image based on the temporary folder
hdiutil create -volname "RMBG2" -srcfolder build_dmg -ov -format UDZO RMBG2.dmg

# (Optional) Clean up the temporary directory
rm -rf build_dmg
rm -rf build
rm -rf dist
```

*This command will generate a standard `RMBG2.dmg` in the current directory. Once opened, you can drag the App into your Applications folder.*
