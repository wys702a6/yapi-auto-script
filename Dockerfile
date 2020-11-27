FROM python:3.7

WORKDIR /workspace
ADD . /workspace
RUN python3 -m pip install --user pipx \
    && python3 -m pipx ensurepath \
    && export PATH=$PATH:/root/.local/bin \
    && pipx completions \
    && pipx install poetry \
    && poetry install

EXPOSE 4444

CMD ["python", "main.py"]