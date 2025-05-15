import pathlib
import socket
import struct

HOST = "127.0.0.1"      # IP сервера
PORT = 5001             # Порт сервера
FILE = r"D:\Elixir Apps\25.6demo.txt"      # Файл, який надсилаємо

def main():
    file_path = pathlib.Path(FILE)
    if not file_path.is_file():
        raise SystemExit(f"Файл «{file_path}» не знайдено")

    filename_bytes = file_path.name.encode("utf-8")
    filesize = file_path.stat().st_size

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(struct.pack("!I", len(filename_bytes)))
        s.sendall(filename_bytes)
        s.sendall(struct.pack("!Q", filesize))
        with open(file_path, "rb") as f:
            while (chunk := f.read(65536)):
                s.sendall(chunk)

    print(f"✔ Файл «{file_path.name}» ({filesize} байт) відправлено → "
          f"{HOST}:{PORT}")

if __name__ == "__main__":
    main()