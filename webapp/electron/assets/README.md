# Assets Directory

Place your application icon here:

- `icon.png` (512x512 or larger, PNG format)
- `icon.ico` (Windows icon, can be generated from PNG)

## Generating Icons

### From PNG to ICO (Windows)

You can use online tools:
- https://convertio.co/png-ico/
- https://icoconvert.com/

Or use ImageMagick:
```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

### Recommended Sizes

- **PNG**: 512x512 px (or 1024x1024 for high-DPI)
- **ICO**: Multi-resolution (16, 32, 48, 64, 128, 256)

## Icon Guidelines

For the Pulox app, consider:
- 🎓 Education theme
- 🎤 Microphone/audio symbol
- 🌐 Language/translation indication
- Simple, recognizable design
- Works at small sizes (16x16)

## Temporary Solution

Until you create a custom icon, the app will use the default Electron icon.
