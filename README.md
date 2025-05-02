```
pip install -r requirements.txt
python -m app.main
```

Либо через Docker
```
docker build -t <IMAGENAME>
docker run -v \ 
  "$(pwd)/settings.json:/home/appuser/app/settings.json:ro" \
  <IMAGENAME>
```