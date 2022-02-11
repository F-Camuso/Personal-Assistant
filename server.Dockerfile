FROM rasa/rasa-sdk:3.0.2
WORKDIR /app

USER root
COPY actions/requirements-actions.txt ./
RUN pip install -r requirements-actions.txt

COPY ./actions /app/actions

USER 1001