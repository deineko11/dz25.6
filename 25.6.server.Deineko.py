import argparse
import os
import pathlib
import socket
import struct
import threading


def handle_client(conn: socket.socket, addr, dest_dir: pathlib.Path):
    try:
        # 1) довжина імені
        raw = conn.recv(4)
        if len(raw) < 4:
            print(f"[{addr}] Неправильний заголовок")
            return
        name_len = struct.unpack("!I", raw)[0]

        # 2) саме ім'я
        filename = conn.recv(name_len).decode("utf-8", "replace")
        safe_name = pathlib.Path(filename).name                    # без каталогів

        # 3) розмір файлу
        size_raw = conn.recv(8)
        if len(size_raw) < 8:
            print(f"[{addr}] Неправильний заголовок (розмір)")
            return
        filesize = struct.unpack("!Q", size_raw)[0]

        # 4) власне файл
        dest_path = dest_dir / safe_name
        remaining = filesize
        with open(dest_path, "wb") as f:
            while remaining:
                chunk = conn.recv(min(65536, remaining))
                if not chunk:
                    raise ConnectionError("Неочікуване розривання з'єднання")
                f.write(chunk)
                remaining -= len(chunk)

        print(f"[{addr}] Отримано «{safe_name}» ({filesize} байт) → {dest_path}")
    except Exception as e:
        print(f"[{addr}] ПОМИЛКА: {e}")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser(description="Простий файловий сервер")
    ap.add_argument("--host", default="0.0.0.0", help="Адреса для прослуховування (за замовч. усі інтерфейси)")
    ap.add_argument("--port", type=int, default=5001, help="Порт (за замовч. 5001)")
    ap.add_argument("--dest", default="uploads", help="Каталог для збереження файлів")
    args = ap.parse_args()

    dest_dir = pathlib.Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.bind((args.host, args.port))
        srv.listen()
        print(f"Сервер слухає {args.host}:{args.port}. Файли → {dest_dir.resolve()}")
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client, args=(conn, addr, dest_dir), daemon=True).start()


if __name__ == "__main__":
    main()