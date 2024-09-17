# FastAPI Application
## Requirements
Make sure you have the following installed on your system:

-   [Install](https://www.python.org/downloads/) Python 3.10 
-   [Install](https://www.docker.com/products/docker-desktop/) Docker

## Part 1: Import the datas 
- Make sure you import all necessary libraries using pip in the terminal 
- Make sure you have enviroment
- Run datas.ipynb file
- Take all datas data.json successfully
- You can check total companies with test.ipynb ( Not necessary )

## Part 2: API connection with port and clustering
- Make sure make the connections 
```
pip install celery
celery -A celery1 worker --loglevel=info
```
```
pip install redis
ps aux | grep redis
kill -9 PID
```
- Using 6380 Port for connection to redis, built a server
```
redis-server --port 6380
```
- Using Analyze.py, make clusters and using LLM model for cluster descriptions
- Make sure you have google gemini key and url
- [Get API Key](https://aistudio.google.com/app/apikey?hl=tr)
  
## Part 3: FastAPI implementation and visualization
- Using Docker make project and built up
```
docker-compose up —build
```
- Built FastAPI to the port
```
uvicorn main2:app --host 0.0.0.0 --port 8000
```
- Make sure you have connection with redis and celery
## Part 4: FastAPI APP
- Open Google and try to make HTTP connections
<details>
<summary> Endpoints in app <summary> 
```
http://0.0.0.0:8000/docs#/
```
- Other Endpoints
```
http://0.0.0.0:8000/assign-cluster-names/
http://127.0.0.1:8000/fetch-data-by-name/
http://0.0.0.0:8000/analyze-data/
```
