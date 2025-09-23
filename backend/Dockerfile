#Slim Python Base
FROM python:3.11-slim

#Working Dir
WORKDIR /app

#Dependancies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy the source code
COPY . /app/

#Run the app with hot-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]