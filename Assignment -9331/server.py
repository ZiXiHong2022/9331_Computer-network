import socket
import threading
import random
import time

server_port = 54321

file_path = 'master.txt'

# 创建 UDP 套接字并绑定到指定端口
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', server_port))

# 读取主文件并初始化缓存
def load_file(file_path):
    in_cache = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                domain, record_type, value = parts
                if domain not in in_cache:
                    in_cache[domain] = []
                in_cache[domain].append((record_type, value))
    return in_cache

in_cache = load_file(file_path)

# 处理客户端请求
def handle_client(data, addr):
    Question_section = data.decode().strip()
    Qid, Qname, Qtype = Question_section.split('\n ')
    
    delay_time = random.randint(0, 4)
    server_log("rcv", addr, Qid, Qname, Qtype, delay_time)
    time.sleep(delay_time)  # 模拟延迟

    response = query_process(Qname, Qtype)
    response_data = str(response)
    server_socket.sendto(response_data.encode(), addr)
    server_log("snd", addr, Qid, Qname, Qtype)

def query_process(Qname, Qtype):
    Answer_section = []
    Authority_section = set()
    Additional_section = set()
    
    def recursive_query(Qname, Qtype, processed_records=set()):
        while True:
            if Qname in in_cache:
                found_match = False
                for rtype, rvalue in in_cache[Qname]:
                    record = f"{Qname},{rtype},{rvalue}"
                    if record not in processed_records:
                        processed_records.add(record)
                        if Qtype == rtype:
                            Answer_section.append(record)
                            found_match = True
                            break  # Exit the loop after finding the match
                        else:
                            if rtype == 'CNAME':
                                Answer_section.append(record)
                                recursive_query(rvalue, Qtype, processed_records)
                                found_match = True
                                break
                if not found_match:
                    break  # Exit the loop if no matching record is found
            else:
                parts = Qname.split(".")
                for i in range(len(parts)):
                    s = ".".join(parts[i:])
                    if s in in_cache and 'NS' in [rec[0] for rec in in_cache[s]]:
                        for rec_type, rec_value in in_cache[s]:
                            if rec_type == 'NS':
                                Authority_section.add((s, 'NS', rec_value))
                                sub_domain = rec_value
                                # 查找额外的 A 记录
                                if sub_domain in in_cache and 'A' in [rec[0] for rec in in_cache[sub_domain]]:
                                    for rec_type, rec_value in in_cache[sub_domain]:
                                        if rec_type == 'A':
                                            Additional_section.add((sub_domain, 'A', rec_value))
                                            break
                        break
                break

    recursive_query(Qname, Qtype)

    if not Answer_section:
        root_domain = '.'
        ns_key = root_domain
        if ns_key in in_cache:
            for ns_record in in_cache[ns_key]:
                if (root_domain, 'NS', ns_record[1]) not in Authority_section:
                    Authority_section.add((root_domain, 'NS', ns_record[1]))
                a_key = ns_record[1]
                if a_key in in_cache:
                    for a_record in in_cache[a_key]:
                        if (ns_record[1], 'A', a_record[1]) not in Additional_section:
                            Additional_section.add((ns_record[1], 'A', a_record[1]))
    
    response = {
        "query": Qname,
        "answer": list(Answer_section),
        "authority": list(Authority_section),
        "additional": list(Additional_section)
    }
    return response

def server_log(action, addr, qid, qname, qtype, delay=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    milliseconds = int((time.time() - int(time.time())) * 1000)
    client_port = addr[1]
    log = f"{timestamp}.{milliseconds:03d} {action} {client_port}: {qid} {qname} {qtype}"
    if delay is not None:
        log += f" (delay: {delay}s)"
    print(log)

def main():
    while True:
        data, addr = server_socket.recvfrom(1024)
        threading.Thread(target=handle_client, args=(data, addr)).start()

if __name__ == "__main__":
    main()
