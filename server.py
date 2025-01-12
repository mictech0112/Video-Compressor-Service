import json
import socket
import subprocess
import os

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 9001))
    sock.listen(1)
    
    while True:
        connection, _ = sock.accept()
        try:
            connection.send('Start the Video Compressor Service.'.encode('utf-8'))

            data = connection.recv(1024).decode('utf-8')
            data_json = json.loads(data)
            filename = data_json['filename']
            filesize = data_json['filesize']
            print(f'filename: {filename}, filesize: {filesize}')

            if filesize == 0:
                raise Exception('No data to read from client.')

            # Upload the file to the server
            with open(os.path.join('input', filename), 'wb+') as f:
                while filesize > 0:
                    data = connection.recv(1400)
                    f.write(data)
                    filesize -= len(data)

            connection.send('Upload finished'.encode('utf-8'))

            while True:
                # Execute Video Compressor Service
                cmd_str = connection.recv(1024).decode('utf-8')
                subprocess.run(cmd_str.split())

                connection.send('File generated.
'.encode('utf-8'))

                # Ask if the service should continue
                continue_question = connection.recv(1024).decode('utf-8')
                if continue_question == '0':
                    os.remove(os.path.join('input', filename))
                    connection.send('End the Video Compressor Service.'.encode('utf-8'))
                    break

        except Exception as e:
            print('Error: ' + str(e))

        finally:
            print('Closing current connection')
            connection.close()

if __name__ == '__main__':
    main()
