import os
import requests
from bs4 import BeautifulSoup
import openai


OPENAI_API_KEY =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


def get_question(session, url):
    """
    Pobiera HTML strony i wyciąga pytanie zabezpieczające.
    Korzystamy z BeautifulSoup, aby znaleźć etykietę zawierającą tekst 'Question:'.
    """
    resp = session.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Znajdź element <label> lub <p> zawierający 'Question:'
    question_container = soup.find(lambda tag: tag.name in ['label', 'p', 'div'] and 'Question:' in tag.get_text())
    if question_container:
        # Usuwamy prefix 'Question:' i zwracamy samą treść pytania
        text = question_container.get_text().strip()
        question = text.split('Question:')[-1].strip()
        return question

    raise ValueError("Nie znaleziono pytania na stronie")


def solve_question(question):
    """
    Wysyła pytanie do modelu LLM przez API OpenAI i zwraca odpowiedź.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("Brak ustawionego klucza OPENAI_API_KEY")

    response = openai.Completion.create(
        model="gpt-4o-nano",  # lub inny dostępny model
        prompt=question,
        max_tokens=50,
        temperature=0
    )
    return response.choices[0].text.strip()


def login_and_fetch_secret(session, url, username, password, answer):
    """
    Wysyła dane do formularza logowania i pobiera zawartość tajnej podstrony.
    """
    payload = {
        'username': username,
        'password': password,
        'answer': answer
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    post_resp = session.post(url, data=payload, headers=headers)
    post_resp.raise_for_status()

    # Serwer zwraca URL do sekretnej podstrony lub pełną treść
    text = post_resp.text.strip()
    if text.startswith('http'):
        secret_url = text
    else:
        # Spróbuj znaleźć w HTML link do sekretnej podstrony
        soup = BeautifulSoup(text, 'html.parser')
        link = soup.find('a', href=True)
        if link:
            secret_url = requests.compat.urljoin(url, link['href'])
        else:
            # Jeśli nie ma URL, zwracamy całą odpowiedź
            return text

    secret_resp = session.get(secret_url)
    secret_resp.raise_for_status()
    return secret_resp.text


def main():
    base_url = "https://xyz.ag3nts.org/"
    username = "tester"
    password = "574e112a"

    with requests.Session() as session:
        question = get_question(session, base_url)
        print(f"Pobrane pytanie: {question}")

        answer = solve_question(question)
        print(f"Odpowiedź z LLM: {answer}")

        secret_content = login_and_fetch_secret(session, base_url, username, password, answer)
        print("--- ZAWARTOŚĆ TAJNEJ PODSTRONY ---")
        print(secret_content)

if __name__ == '__main__':
    main()
