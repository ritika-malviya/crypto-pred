FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE $PORT
CMD ["streamlit","run","streamlit_app.py","--server.port = 8501","--server.address = 0.0.0.0"]
 
