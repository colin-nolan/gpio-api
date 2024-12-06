# GPIO API

To run on a Raspberry Pi 5:
```
sudo GPIOZERO_PIN_FACTORY=lgpio GPIO_API_DATABASE_URL='sqlite:////tmp/gpio.db' GPIO_API_USERNAME=123 GPIO_API_PASSWORD=456 .venv/bin/fastapi run --host 0.0.0.0 src/gpio_api/app.py
```

In Docker:
```
docker build -t colinnolan/gpio-api .
```
```
docker run --rm -d -p 8000:80 --device /dev/gpiochip4 colinnolan/gpio-api
```
