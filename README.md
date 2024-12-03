# GPIO API

To run on a Raspberry Pi 5:
```
sudo GPIOZERO_PIN_FACTORY=lgpio .venv/bin/fastapi dev --host 0.0.0.0 src/gpio_api/app.py
```

In Docker:
```
docker build -t colinnolan/gpio-api .
```
```
docker run --rm -d -p 8000:80 --device /dev/gpiochip4 colinnolan/gpio-api
```
