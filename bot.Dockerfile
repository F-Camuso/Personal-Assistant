FROM rasa/rasa:3.0.4-full

USER root

RUN python -m spacy download pt_core_news_md

USER 1001