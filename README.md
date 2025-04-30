```
pip install -r requirements.txt
python -m app.main
```

Либо через Docker
```
docker build -t <image_name>
docker run --env-file .env <image_name>
```