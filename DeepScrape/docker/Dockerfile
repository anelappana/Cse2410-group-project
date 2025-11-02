FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["bash","-lc","python scripts/run_crawl.py --urls https://example.com --keywords court --fields title,url"]
